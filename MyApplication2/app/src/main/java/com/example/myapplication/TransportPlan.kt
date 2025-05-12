package com.example.myapplication

import kotlinx.parcelize.Parcelize

@Parcelize
data class TransportPlan(
    val transports: List<List<TransportationItem>>
) : Transportation() {
    override fun getAllTransports(): List<TransportationItem> = transports.flatten()
}
