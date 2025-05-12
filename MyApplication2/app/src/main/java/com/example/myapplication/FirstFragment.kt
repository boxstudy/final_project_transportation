package com.example.myapplication

import android.app.TimePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.navigation.Navigation
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import okhttp3.*
import java.io.IOException
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.util.*

class FirstFragment : Fragment() {

    private var selectedDate: String? = null
    private var selectedTime: String? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_first, container, false)

        val stationMap = mapOf(
            "台鐵" to resources.getStringArray(R.array.stations_tra).toList(),
            "高鐵" to resources.getStringArray(R.array.stations_hsr).toList(),
            "東華大學" to resources.getStringArray(R.array.stations_ndhu).toList()
        )

        val sButton = view.findViewById<Button>(R.id.btn_set_location)
        val endSelector = view.findViewById<TextView>(R.id.end_seletor)
        val btnPickDate = view.findViewById<ImageButton>(R.id.pickDateImageButton)
        val btnPickTime = view.findViewById<ImageButton>(R.id.pickDateImageButton2)
        val textViewDate = view.findViewById<TextView>(R.id.time_text)
        val textViewTime = view.findViewById<TextView>(R.id.editTextText)
        val startSelector = view.findViewById<TextView>(R.id.start_seletor)

        sButton.setOnClickListener {
            val startStation = startSelector.text.toString()
            val endStation = endSelector.text.toString()

            if (!selectedDate.isNullOrEmpty() && !selectedTime.isNullOrEmpty()) {
                val departureTime = "$selectedDate $selectedTime"

                sendDataToPythonServer(departureTime, startStation, endStation) { transportPlans ->
                    requireActivity().runOnUiThread {
                        val bundle = Bundle()
                        bundle.putParcelableArrayList("transport_list", ArrayList(transportPlans))
                        Navigation.findNavController(view).navigate(
                            R.id.action_firstFragment_to_secondFragment,
                            bundle
                        )
                    }
                }
            } else {
                Toast.makeText(requireContext(), "請選擇完整的出發日期與時間", Toast.LENGTH_SHORT).show()
            }
        }

        btnPickDate.setOnClickListener {
            val calendar = Calendar.getInstance()
            val year = calendar.get(Calendar.YEAR)
            val month = calendar.get(Calendar.MONTH)
            val day = calendar.get(Calendar.DAY_OF_MONTH)

            val datePickerDialog = android.app.DatePickerDialog(
                requireContext(),
                { _, selectedYear, selectedMonth, selectedDay ->
                    selectedDate = String.format(Locale.getDefault(), "%04d-%02d-%02d", selectedYear, selectedMonth + 1, selectedDay)
                    textViewDate.text = selectedDate
                }, year, month, day
            )
            datePickerDialog.show()
        }

        btnPickTime.setOnClickListener {
            val calendar = Calendar.getInstance()
            val hour = calendar.get(Calendar.HOUR_OF_DAY)
            val minute = calendar.get(Calendar.MINUTE)

            val timePickerDialog = TimePickerDialog(
                requireContext(),
                { _, selectedHour, selectedMinute ->
                    selectedTime = String.format(Locale.getDefault(), "%02d:%02d", selectedHour, selectedMinute)
                    textViewTime.text = selectedTime
                }, hour, minute, true
            )
            timePickerDialog.show()
        }

        startSelector.setOnClickListener {
            showStationPicker(stationMap) { selected -> startSelector.text = selected }
        }

        endSelector.setOnClickListener {
            showStationPicker(stationMap) { selected -> endSelector.text = selected }
        }

        return view
    }

    private fun sendDataToPythonServer(
        departureTime: String,
        startStation: String,
        endStation: String,
        callback: (List<TransportPlan>) -> Unit
    ) {
        val client = OkHttpClient()

        val encodedTime = URLEncoder.encode(departureTime, StandardCharsets.UTF_8.toString()).replace("+", "%20")
        val encodedStart = URLEncoder.encode(startStation, StandardCharsets.UTF_8.toString())
        val encodedEnd = URLEncoder.encode(endStation, StandardCharsets.UTF_8.toString())

        val url = "http://134.208.32.97:8888/data/recommend$encodedTime" +
                "_$encodedStart" +
                "_$encodedEnd"

        val request = Request.Builder().url(url).get().build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                callback(emptyList())
            }

            override fun onResponse(call: Call, response: Response) {
                response.body?.string()?.let { responseBody ->
                    val gson = Gson()

                    try {
                        val path: List<List<List<TransportationItem>>> = gson.fromJson(
                            responseBody,
                            object : TypeToken<List<List<List<TransportationItem>>>>() {}.type
                        )
                        val transportPlans = path.map { TransportPlan(it) }
                        callback(transportPlans)
                        return
                    } catch (_: Exception) {}

                    try {
                        val path: List<List<TransportationItem>> = gson.fromJson(
                            responseBody,
                            object : TypeToken<List<List<TransportationItem>>>() {}.type
                        )
                        val transportPlans = path.map { TransportPlan(listOf(it)) }
                        callback(transportPlans)
                        return
                    } catch (_: Exception) {}

                    try {
                        val path: List<TransportationItem> = gson.fromJson(
                            responseBody,
                            object : TypeToken<List<TransportationItem>>() {}.type
                        )
                        val transportPlans = listOf(TransportPlan(listOf(path)))
                        callback(transportPlans)
                        return
                    } catch (e: Exception) {
                        e.printStackTrace()
                        callback(emptyList())
                    }
                }
            }
        })
    }


    private fun showStationPicker(
        stationMap: Map<String, List<String>>,
        onStationSelected: (String) -> Unit
    ) {
        val types = stationMap.keys.toTypedArray()

        AlertDialog.Builder(requireContext())
            .setTitle("選擇類型")
            .setItems(types) { _, which ->
                val selectedType = types[which]
                val stations = stationMap[selectedType] ?: emptyList()

                AlertDialog.Builder(requireContext())
                    .setTitle("選擇站點")
                    .setItems(stations.toTypedArray()) { _, stationIndex ->
                        val selectedStation = stations[stationIndex]
                        onStationSelected(selectedStation)
                    }
                    .show()
            }
            .show()
    }
}
