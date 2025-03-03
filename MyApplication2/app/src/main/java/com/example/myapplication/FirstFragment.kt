package com.example.myapplication

import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import org.json.JSONObject
import java.io.IOException
import android.app.DatePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.navigation.Navigation
import java.util.Calendar
import okhttp3.MediaType.Companion.toMediaTypeOrNull


class FirstFragment : Fragment() {
    private lateinit var tvSelectedDate: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_first, container, false)
        val sButton = view.findViewById<Button>(R.id.btn_set_location)
        val editText = view.findViewById<EditText>(R.id.spinner)
        val editText2 = view.findViewById<EditText>(R.id.spinner2)
        val buttonSend = view.findViewById<Button>(R.id.button)
        val textViewResult = view.findViewById<TextView>(R.id.textView17)

        buttonSend.setOnClickListener {
            val userInput = editText.text.toString()
            val userInput2 = editText2.text.toString()
            sendDataToPythonServer(userInput, userInput2) { response ->
                requireActivity().runOnUiThread {
                    textViewResult.text = response  // 顯示 Python 回傳的結果
                }
            }

        }

        sButton.setOnClickListener {
            Navigation.findNavController(view).navigate(R.id.action_firstFragment_to_secondFragment)
        }

        val btnPickDate = view.findViewById<ImageButton>(R.id.pickDateImageButton)
        tvSelectedDate = view.findViewById(R.id.selected_date)
        btnPickDate.setOnClickListener {
            showDatePicker()
        }

        return view
    }

    private fun showDatePicker() {
        val calendar = Calendar.getInstance()
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH)

        val datePicker = DatePickerDialog(requireContext(), { _, selectedYear, selectedMonth, selectedDay ->
            val date = "$selectedYear-${selectedMonth + 1}-$selectedDay"
            tvSelectedDate.text = date
        }, year, month, day)

        datePicker.show()
    }

    private fun sendDataToPythonServer(input1: String, input2: String, callback: (String) -> Unit) {
        val client = OkHttpClient()
        val json = JSONObject().apply {
            put("input1", input1)
            put("input2", input2)
         }.toString()

        val mediaType = "application/json".toMediaTypeOrNull()
        val body = RequestBody.create(mediaType, json)

        val request = Request.Builder()
            .url("http://134.208.32.97:8888/process_data")  // 替換為你的 Python 伺服器 IP
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                callback("請求失敗: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                val body = response.body  // ✅ 先存起來，避免多次調用
                body?.let {
                    val responseData = JSONObject(it.string()).getString("result")
                    callback(responseData)
                }
            }

        })
    }

}
