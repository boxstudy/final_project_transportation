package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.TimeUnit

class TransportationAdapter(
    private var data: List<Transportation>,
    private val onItemClick: (Transportation) -> Unit
) : RecyclerView.Adapter<TransportationAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val routeText: TextView = view.findViewById(R.id.routeText)
        val timeText: TextView = view.findViewById(R.id.timeText)
        val typeText: TextView = view.findViewById(R.id.typeText)
        val costText: TextView = view.findViewById(R.id.costText)
        val durationText: TextView = view.findViewById(R.id.durationText)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_transportation, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = data.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = data[position]
        val transports = item.getAllTransports()

        val departureRaw = transports.firstOrNull()?.departure_time
        val arrivalRaw = transports.lastOrNull()?.arrival_time
        val inputFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
        val outputFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        val departureFormatted = try {
            inputFormat.parse(departureRaw ?: "")?.let { outputFormat.format(it) } ?: departureRaw.orEmpty()
        } catch (e: Exception) {
            departureRaw.orEmpty()
        }

        val arrivalFormatted = try {
            inputFormat.parse(arrivalRaw ?: "")?.let { outputFormat.format(it) } ?: arrivalRaw.orEmpty()
        } catch (e: Exception) {
            arrivalRaw.orEmpty()
        }

        holder.routeText.text = "${transports.firstOrNull()?.departure_place} → ${transports.lastOrNull()?.arrival_place}"
        holder.timeText.text = "$departureFormatted ~ $arrivalFormatted"

        if (transports.size > 1) {
            holder.typeText.text = "🚉 轉乘"
            holder.typeText.setTextColor(ContextCompat.getColor(holder.itemView.context, R.color.sky_blue))
        } else {
            val transport = transports.firstOrNull()
            val type = transport?.type ?: ""
            val icon = when (type.lowercase()) {
                "expresstrain" -> "🚆"
                "highspeedrail" -> "🚄"
                "bus" -> "🚌"
                else -> "🚙"
            }
            val label = when (type.lowercase()) {
                "expresstrain" -> "台鐵對號座"
                "highspeedrail" -> "高鐵"
                "bus" -> "公車"
                else -> "其他"
            }
            val colorRes = when (type.lowercase()) {
                "expresstrain" -> R.color.teal_700
                "highspeedrail" -> R.color.purple2
                "bus" -> R.color.green
                else -> R.color.gray
            }

            val trainNumber = transport?.transportation_name ?: transport?.train_number ?: ""
            holder.typeText.text = if (trainNumber.isNotBlank()) "$icon $label（$trainNumber）" else "$icon $label"
            holder.typeText.setTextColor(ContextCompat.getColor(holder.itemView.context, colorRes))
        }
        fun parseCost(cost: Any?): Int {
            return when (cost) {
                is Number -> cost.toInt()
                is String -> {
                    cost.replace(",", "").toIntOrNull() ?: 0
                }
                else -> 0
            }
        }

        val times = transports.mapNotNull {
            try {
                val dep = inputFormat.parse(it.departure_time ?: "")
                val arr = inputFormat.parse(it.arrival_time ?: "")
                if (dep != null && arr != null) Pair(dep, arr) else null
            } catch (e: Exception) {
                null
            }
        }

        val totalRideMinutes = times.sumOf { (start, end) ->
            TimeUnit.MILLISECONDS.toMinutes(end.time - start.time)
        }

        val totalWaitMinutes = times.zipWithNext { a, b ->
            TimeUnit.MILLISECONDS.toMinutes(b.first.time - a.second.time)
        }.sum()

        val durationText = if (transports.size > 1)
            "乘車時間：${totalRideMinutes} 分鐘｜等待：${totalWaitMinutes} 分鐘"
        else
            "乘車時間：${totalRideMinutes} 分鐘"

        holder.durationText.text = durationText
        holder.costText.text = "票價：$${transports.sumOf { parseCost(it.cost) }}"

        holder.itemView.setOnClickListener {
            onItemClick(item)
        }
    }

    fun updateData(newData: List<Transportation>) {
        data = newData
        notifyDataSetChanged()
    }
}
