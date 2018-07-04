package com.dscvit.smartglasscompanion

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class KillReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        context?.startService(Intent(context, NotificationListenerFirebase::class.java))
    }
}