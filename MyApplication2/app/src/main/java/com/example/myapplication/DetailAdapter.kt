package com.example.myapplication

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.*

class DetailAdapter(private val transports: List<TransportationItem>) :
    RecyclerView.Adapter<DetailAdapter.DetailViewHolder>() {

    class DetailViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val routeText: TextView = view.findViewById(R.id.routeText)
        val timeText: TextView = view.findViewById(R.id.timeText)
        val typeText: TextView = view.findViewById(R.id.typeText)
        val costText: TextView = view.findViewById(R.id.costText)
        val durationText: TextView = view.findViewById(R.id.durationText)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DetailViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_detail, parent, false)
        return DetailViewHolder(view)
    }

    override fun onBindViewHolder(holder: DetailViewHolder, position: Int) {
        val transport = transports[position]

        holder.routeText.text = "${transport.departure_place} → ${transport.arrival_place}"

        val inputFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
        val outputFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        val depTime = try { inputFormat.parse(transport.departure_time) } catch (e: Exception) { null }
        val arrTime = try { inputFormat.parse(transport.arrival_time) } catch (e: Exception) { null }

        val depText = depTime?.let { outputFormat.format(it) } ?: transport.departure_time
        val arrText = arrTime?.let { outputFormat.format(it) } ?: transport.arrival_time
        holder.timeText.text = "$depText ~ $arrText"

        val duration = if (depTime != null && arrTime != null) {
            ((arrTime.time - depTime.time) / 60000).toInt()
        } else null
        holder.durationText.text = duration?.let { "乘車時間：$it 分鐘" } ?: ""

        val type = transport.type?.lowercase()
        val icon = when (type) {
            "expresstrain" -> "🚆"
            "highspeedrail" -> "🚄"
            "bus" -> "🚌"
            else -> "🚙"
        }
        val label = when (type) {
            "expresstrain" -> "台鐵對號座"
            "highspeedrail" -> "高鐵"
            "bus" -> "公車"
            else -> "其他"
        }
        val trainNumber = transport.transportation_name ?: transport.train_number ?: ""
        holder.typeText.text = "$icon $label${if (trainNumber.isNotBlank()) "（$trainNumber）" else ""}"

        val colorRes = when (type) {
            "expresstrain" -> R.color.teal_700
            "highspeedrail" -> R.color.purple2
            "bus" -> R.color.green
            else -> R.color.gray
        }
        holder.typeText.setTextColor(ContextCompat.getColor(holder.itemView.context, colorRes))

        holder.costText.text = "票價：$${transport.cost ?: 0}"
    }

    override fun getItemCount(): Int = transports.size
}
