package com.dscvit.smartglasscompanion

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import com.google.firebase.database.FirebaseDatabase

class NotificationListenerFirebase : NotificationListenerService() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        onTaskRemoved(intent)
        return Service.START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        return super.onBind(intent)
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
//        val intent = Intent("com.dscvit.smartglasscompanion")
//        intent.putExtra("SAMPLE_NOTIF", sbn?.notification?.toString())
//        sendBroadcast(intent)

        var pack = ""
        var text = ""
        var title = ""
        var id = 0

        sbn?.let {sbn ->
            pack = sbn.packageName
            id = sbn.id

            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.KITKAT) {
                val extras = sbn.notification.extras
                text = extras.getCharSequence("android.text").toString()
                title = extras.getString("android.title")
            }

            Log.i("NOTIF_PACK", pack)
            Log.i("NOTIF_TITLE", title)
            Log.i("NOTIF_TEXT", text)
        }

        val dbInstance = FirebaseDatabase.getInstance().getReference("notifs").child(pack.replace(".", ""))
        with(dbInstance) {
            child("package").setValue(pack)
            child("title").setValue(title)
            child("text").setValue(text)
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {

    }

//    override fun onDestroy() {
//        super.onDestroy()
//        val intent = Intent("com.dscvit.smartglasscompanion")
//        sendBroadcast(intent)
//    }

    override fun onTaskRemoved(rootIntent: Intent?) {
        val restartServiceIntent = Intent(applicationContext, javaClass)
        restartServiceIntent.setPackage(packageName)
        startService(restartServiceIntent)
        super.onTaskRemoved(rootIntent)
    }

}