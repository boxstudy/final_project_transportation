package com.example.myapplication

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.navigation.Navigation
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.os.Parcelable
import androidx.appcompat.app.AlertDialog

class SecondFragment : Fragment() {

    private lateinit var adapter: TransportationAdapter
    private var originalList: List<Transportation> = emptyList()
    private var displayedList: List<Transportation> = emptyList()
    private var isAscending = true
    private val selectedTypes = mutableSetOf<String>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_second, container, false)

        val routeList = arguments?.getParcelableArrayList<Transportation>("transport_list") ?: emptyList()
        originalList = routeList
        displayedList = routeList

        val spinner = view.findViewById<Spinner>(R.id.spinner_sort)
        val recyclerView = view.findViewById<RecyclerView>(R.id.recyclerViewList)
        recyclerView.layoutManager = LinearLayoutManager(requireContext())

        adapter = TransportationAdapter(displayedList) { selectedRoute ->
            val bundle = Bundle()
            if (selectedRoute is Parcelable) {
                bundle.putParcelable("selected_route", selectedRoute)
            }
            Navigation.findNavController(view).navigate(R.id.action_secondFragment_to_detailFragment, bundle)
        }
        recyclerView.adapter = adapter

        val sortButton = view.findViewById<Button>(R.id.sortOrderButton)
        sortButton.setOnClickListener {
            isAscending = !isAscending
            sortButton.text = if (isAscending) "升序" else "降序"
            applySorting(spinner.selectedItemPosition)
        }

        spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>, view: View?, position: Int, id: Long) {
                applySorting(position)
            }
            override fun onNothingSelected(parent: AdapterView<*>) {}
        }

        view.findViewById<Button>(R.id.filterTypeButton).setOnClickListener {
            showTypeFilterDialog()
        }

        view.findViewById<ImageButton>(R.id.backimageButton).setOnClickListener {
            Navigation.findNavController(view).navigate(R.id.action_secondFragment_to_firstFragment)
        }

        return view
    }

    private fun applySorting(position: Int) {
        var tempList = displayedList
        tempList = when (position) {
            0 -> if (isAscending) tempList.sortedBy { it.getAllTransports().sumOf { t -> t.cost ?: 0 } }
            else tempList.sortedByDescending { it.getAllTransports().sumOf { t -> t.cost ?: 0 } }
            1 -> if (isAscending) tempList.sortedBy { it.getAllTransports().firstOrNull()?.departure_time ?: "9999-99-99 99:99" }
            else tempList.sortedByDescending { it.getAllTransports().firstOrNull()?.departure_time ?: "0000-00-00 00:00" }
            2 -> if (isAscending) tempList.sortedBy { it.getAllTransports().lastOrNull()?.arrival_time ?: "9999-99-99 99:99" }
            else tempList.sortedByDescending { it.getAllTransports().lastOrNull()?.arrival_time ?: "0000-00-00 00:00" }
            3 -> if (isAscending) tempList.sortedBy { it.getAllTransports().size - 1 }
            else tempList.sortedByDescending { it.getAllTransports().size - 1 }
            else -> tempList
        }
        adapter.updateData(tempList)
    }

    private fun showTypeFilterDialog() {
        val allTypes = listOf("台鐵對號座", "高鐵", "公車", "轉乘")
        val checkedItems = allTypes.map { selectedTypes.contains(it) }.toBooleanArray()

        AlertDialog.Builder(requireContext())
            .setTitle("選擇要顯示的交通方式")
            .setMultiChoiceItems(allTypes.toTypedArray(), checkedItems) { _, which, isChecked ->
                if (isChecked) selectedTypes.add(allTypes[which])
                else selectedTypes.remove(allTypes[which])
            }
            .setPositiveButton("確定") { _, _ ->
                filterBySelectedTypes()
            }
            .setNegativeButton("取消", null)
            .show()
    }

    private fun filterBySelectedTypes() {
        displayedList = if (selectedTypes.isEmpty()) {
            originalList
        } else {
            originalList.filter { transportation ->
                val transports = transportation.getAllTransports()
                if (transports.size > 1) {
                    "轉乘" in selectedTypes
                } else {
                    val type = transports.firstOrNull()?.type?.lowercase() ?: ""
                    when {
                        type.contains("expresstrain") -> "台鐵對號座" in selectedTypes
                        type.contains("highspeedrail") -> "高鐵" in selectedTypes
                        type.contains("bus") -> "公車" in selectedTypes
                        else -> false
                    }
                }
            }
        }
        applySorting(view?.findViewById<Spinner>(R.id.spinner_sort)?.selectedItemPosition ?: 0)
    }
}
