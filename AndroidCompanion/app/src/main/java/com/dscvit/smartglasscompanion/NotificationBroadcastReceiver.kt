package com.dscvit.smartglasscompanion

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.google.firebase.database.FirebaseDatabase

class NotificationBroadcastReceiver : BroadcastReceiver(){
    override fun onReceive(context: Context?, intent: Intent?) {
        val dbInstance = FirebaseDatabase.getInstance().getReference("notifs")
        dbInstance.push().setValue(intent?.getStringExtra("SAMPLE_NOTIF"))
    }
}