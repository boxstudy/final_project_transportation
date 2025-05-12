package com.example.myapplication

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import androidx.navigation.Navigation
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.os.Parcelable


class DetailFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_detail, container, false)

        val backButton = view.findViewById<ImageButton>(R.id.backButtonDetail)
        val recyclerView = view.findViewById<RecyclerView>(R.id.detailRecyclerView)

        val selectedRoute = arguments?.getParcelable<Parcelable>("selected_route")

        val transportList = when (selectedRoute) {
            is Route -> selectedRoute.transports
            is TransportPlan -> selectedRoute.transports.flatten()
            else -> emptyList()
        }


        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = DetailAdapter(transportList)

        backButton.setOnClickListener {
            Navigation.findNavController(view).navigateUp()
        }

        return view
    }
}
