package com.example.myapplication

import kotlinx.parcelize.Parcelize
import android.os.Parcelable

@Parcelize
data class TransportationItem(
    val type: String?,
    val departure_place: String?,
    val arrival_place: String?,
    val transportation_name: String?,
    val train_number: String?,
    val departure_time: String?,
    val arrival_time: String?,
    val cost: Int?
) : Parcelable
