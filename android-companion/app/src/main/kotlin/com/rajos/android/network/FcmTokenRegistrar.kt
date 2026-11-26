package com.rajos.android.network

import android.content.Context
import android.util.Log
import com.rajos.android.BuildConfig
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

/**
 * Registers the Firebase Cloud Messaging token with the RajOS backend
 * (POST /notifications/register-fcm-token).
 *
 * The backend accepts an optional `Authorization: Bearer <jwt>` header. When the
 * user has signed in, [saveAuthToken] stores the JWT and it is sent with future
 * registrations; without it the backend falls back to its default user.
 */
object FcmTokenRegistrar {

    private const val TAG = "FcmTokenRegistrar"
    private const val PREFS_NAME = "rajos_auth"
    private const val KEY_AUTH_TOKEN = "auth_token"
    private const val KEY_REGISTERED_TOKEN = "registered_fcm_token"
    private const val CONNECT_TIMEOUT_MS = 10_000
    private const val READ_TIMEOUT_MS = 10_000

    private val executor = Executors.newSingleThreadExecutor()

    /** Store the backend JWT so later token registrations are attributed to the user. */
    fun saveAuthToken(context: Context, jwt: String) {
        prefs(context).edit().putString(KEY_AUTH_TOKEN, jwt).apply()
    }

    /** Clear the stored JWT (call on logout). */
    fun clearAuthToken(context: Context) {
        prefs(context).edit().remove(KEY_AUTH_TOKEN).remove(KEY_REGISTERED_TOKEN).apply()
    }

    /**
     * Forget which token was last registered, forcing the next [register] call to
     * re-send it. Used after sign-in so the token is attached to the new user.
     */
    fun invalidateRegistration(context: Context) {
        prefs(context).edit().remove(KEY_REGISTERED_TOKEN).apply()
    }

    /** The stored backend JWT, or null when signed out. */
    fun getAuthToken(context: Context): String? =
        prefs(context).getString(KEY_AUTH_TOKEN, null)

    /**
     * Register [token] with the backend in the background. Safe to call repeatedly:
     * a token that was already accepted is not sent again, and failures are only logged.
     */
    fun register(context: Context, token: String) {
        if (token.isBlank()) return
        val appContext = context.applicationContext
        executor.execute { registerBlocking(appContext, token) }
    }

    private fun registerBlocking(context: Context, token: String) {
        val prefs = prefs(context)
        if (prefs.getString(KEY_REGISTERED_TOKEN, null) == token) {
            Log.d(TAG, "FCM token already registered, skipping")
            return
        }

        // Registration is tied to a signed-in user. currentAccessToken() renews an
        // expired access token from the refresh token, or clears the session and asks
        // for credentials when no valid token can be produced.
        val jwt = AuthRepository.currentAccessToken(context)
        if (jwt == null) {
            Log.d(TAG, "No valid session; skipping FCM token registration")
            return
        }

        val endpoint = "${BuildConfig.BACKEND_BASE_URL}/notifications/register-fcm-token"
        var connection: HttpURLConnection? = null
        try {
            connection = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
                doOutput = true
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Accept", "application/json")
                setRequestProperty("Authorization", "Bearer $jwt")
            }

            val payload = JSONObject().put("token", token).toString()
            connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }

            val code = connection.responseCode
            if (code in 200..299) {
                prefs.edit().putString(KEY_REGISTERED_TOKEN, token).apply()
                Log.i(TAG, "FCM token registered with backend")
            } else {
                val error = connection.errorStream?.bufferedReader()?.use { it.readText() }
                Log.w(TAG, "FCM token registration failed (HTTP $code): $error")
                if (code == HttpURLConnection.HTTP_UNAUTHORIZED) {
                    // Stored JWT is no longer accepted: clear it and ask the user to sign in.
                    AuthRepository.notifySessionExpired(context)
                }
            }
        } catch (e: Exception) {
            // Network failures must not crash the app; retried on the next token refresh.
            Log.w(TAG, "Could not register FCM token with ${BuildConfig.BACKEND_BASE_URL}", e)
        } finally {
            connection?.disconnect()
        }
    }

    private fun prefs(context: Context) =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
}
