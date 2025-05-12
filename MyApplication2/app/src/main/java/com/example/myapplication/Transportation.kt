package com.example.myapplication

import android.os.Parcelable

abstract class Transportation : Parcelable {
    abstract fun getAllTransports(): List<TransportationItem>
}
