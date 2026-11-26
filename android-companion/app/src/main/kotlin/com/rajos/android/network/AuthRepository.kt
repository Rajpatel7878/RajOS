package com.rajos.android.network

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.util.Log
import com.rajos.android.BuildConfig
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

/**
 * Handles authentication against the RajOS backend (POST /login) and persists the
 * returned JWT so authenticated calls (e.g. FCM token registration) can use it.
 */
class AuthRepository(context: Context) {

    private val appContext = context.applicationContext
    private val prefs = appContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val executor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())

    /** Email of the last signed-in user, or null when no session was saved. */
    val currentUserEmail: String?
        get() = prefs.getString(KEY_EMAIL, null)

    /**
     * Restore the saved session, renewing the access token from the refresh token
     * when needed. The callback runs on the main thread with the signed-in email,
     * or null when the session is gone and the user must sign in again.
     */
    fun restoreSession(onResult: (String?) -> Unit) {
        executor.execute {
            val email = prefs.getString(KEY_EMAIL, null)
            val resolved = if (email != null && currentAccessToken(appContext) != null) email else null
            mainHandler.post { onResult(resolved) }
        }
    }

    /**
     * Sign in with [email]/[password]. The callback runs on the main thread and
     * receives the signed-in email on success or a user-facing message on failure.
     */
    fun login(email: String, password: String, onResult: (Result<String>) -> Unit) {
        executor.execute {
            val result = runCatching { loginBlocking(email, password) }
            mainHandler.post { onResult(result) }
        }
    }

    /**
     * Create an account with the backend, then sign in with the same credentials so
     * the app ends up with a JWT (POST /register does not return one).
     * The callback runs on the main thread.
     */
    fun register(
        username: String,
        email: String,
        password: String,
        onResult: (Result<String>) -> Unit
    ) {
        executor.execute {
            val result = runCatching {
                registerBlocking(username, email, password)
                loginBlocking(email, password)
            }
            mainHandler.post { onResult(result) }
        }
    }

    /** Clear the stored session, including the refresh token. */
    fun logout() {
        clearSession(appContext)
    }

    private fun registerBlocking(username: String, email: String, password: String) {
        val endpoint = "${BuildConfig.BACKEND_BASE_URL}/register"
        var connection: HttpURLConnection? = null
        try {
            connection = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
                doOutput = true
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Accept", "application/json")
            }

            val payload = JSONObject()
                .put("username", username)
                .put("email", email)
                .put("password", password)
                .toString()
            connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }

            val code = connection.responseCode
            val body = (if (code in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()
                ?.use { it.readText() }
                .orEmpty()

            if (code !in 200..299) {
                throw IllegalStateException(extractError(body, code))
            }

            Log.i(TAG, "Account created for $email")
        } finally {
            connection?.disconnect()
        }
    }

    private fun loginBlocking(email: String, password: String): String {
        val endpoint = "${BuildConfig.BACKEND_BASE_URL}/login"
        var connection: HttpURLConnection? = null
        try {
            connection = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
                doOutput = true
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Accept", "application/json")
            }

            val payload = JSONObject()
                .put("email", email)
                .put("password", password)
                .toString()
            connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }

            val code = connection.responseCode
            val body = (if (code in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()
                ?.use { it.readText() }
                .orEmpty()

            if (code !in 200..299) {
                throw IllegalStateException(extractError(body, code))
            }

            val token = JSONObject(body).optString("access_token").takeIf { it.isNotBlank() }
                ?: throw IllegalStateException("Login response did not contain an access token")

            val refreshToken = JSONObject(body).optString("refresh_token")
            val editor = prefs.edit().putString(KEY_EMAIL, email)
            if (refreshToken.isNotBlank()) {
                editor.putString(KEY_REFRESH, refreshToken)
            }
            editor.apply()
            FcmTokenRegistrar.saveAuthToken(appContext, token)
            // The FCM token must be re-sent so the backend attaches it to this user.
            FcmTokenRegistrar.invalidateRegistration(appContext)

            Log.i(TAG, "Login succeeded for $email")
            return email
        } finally {
            connection?.disconnect()
        }
    }

    private fun extractError(body: String, code: Int): String {
        val detail = runCatching { JSONObject(body).optString("detail") }.getOrNull()
        return when {
            !detail.isNullOrBlank() -> detail
            code == 401 -> "Wrong password"
            code == 404 -> "User not found"
            code == 400 -> "Registration failed (HTTP 400)"
            else -> "Authentication failed (HTTP $code)"
        }
    }

    companion object {
        private const val TAG = "AuthRepository"
        private const val PREFS_NAME = "rajos_auth"
        private const val KEY_EMAIL = "user_email"
        private const val KEY_REFRESH = "refresh_token"
        private const val CONNECT_TIMEOUT_MS = 10_000
        private const val READ_TIMEOUT_MS = 10_000

        /** Invoked on the main thread when the backend rejects the stored JWT. */
        @Volatile
        var onSessionExpired: (() -> Unit)? = null

        /** Remove the access/refresh tokens, the cached email and the FCM marker. */
        fun clearSession(context: Context) {
            FcmTokenRegistrar.clearAuthToken(context)
            context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .remove(KEY_EMAIL)
                .remove(KEY_REFRESH)
                .apply()
        }

        /**
         * A currently valid access token, silently renewed from the refresh token when
         * the access token has expired. Returns null (and clears the session) when the
         * refresh token is missing, expired or rejected. Safe to call off the main thread.
         */
        fun currentAccessToken(context: Context): String? {
            val access = FcmTokenRegistrar.getAuthToken(context)
            if (access != null && !isTokenExpired(access)) return access

            val refresh = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .getString(KEY_REFRESH, null)
            if (refresh == null || isTokenExpired(refresh)) {
                Log.i(TAG, "No usable refresh token")
                notifySessionExpired(context)
                return null
            }

            val renewed = requestNewTokens(context, refresh)
            if (renewed == null) {
                Log.i(TAG, "Refresh token was rejected")
                notifySessionExpired(context)
            }
            return renewed
        }

        /** POST /refresh; stores and returns the new access token (null on failure). */
        private fun requestNewTokens(context: Context, refreshToken: String): String? {
            val endpoint = "${BuildConfig.BACKEND_BASE_URL}/refresh"
            var connection: HttpURLConnection? = null
            try {
                connection = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = CONNECT_TIMEOUT_MS
                    readTimeout = READ_TIMEOUT_MS
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                    setRequestProperty("Accept", "application/json")
                }

                val payload = JSONObject().put("refresh_token", refreshToken).toString()
                connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }

                val code = connection.responseCode
                val body = (if (code in 200..299) connection.inputStream else connection.errorStream)
                    ?.bufferedReader()
                    ?.use { it.readText() }
                    .orEmpty()

                if (code !in 200..299) {
                    Log.w(TAG, "Token refresh failed (HTTP $code): $body")
                    return null
                }

                val json = JSONObject(body)
                val access = json.optString("access_token").takeIf { it.isNotBlank() } ?: return null
                val rotatedRefresh = json.optString("refresh_token")
                    .takeIf { it.isNotBlank() } ?: refreshToken

                FcmTokenRegistrar.saveAuthToken(context, access)
                context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                    .edit()
                    .putString(KEY_REFRESH, rotatedRefresh)
                    .apply()

                Log.i(TAG, "Access token renewed")
                return access
            } catch (e: Exception) {
                Log.w(TAG, "Could not refresh access token", e)
                return null
            } finally {
                connection?.disconnect()
            }
        }

        /** Called when an authenticated request fails with 401. */
        fun notifySessionExpired(context: Context) {
            clearSession(context)
            val listener = onSessionExpired ?: return
            Handler(Looper.getMainLooper()).post { listener() }
        }

        /** Reads the JWT `exp` claim; malformed tokens are treated as expired. */
        fun isTokenExpired(jwt: String): Boolean {
            return try {
                val parts = jwt.split('.')
                if (parts.size < 2) return true
                val payload = String(
                    Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING),
                    Charsets.UTF_8
                )
                val expSeconds = JSONObject(payload).optLong("exp", 0L)
                expSeconds <= 0L || expSeconds * 1000L <= System.currentTimeMillis()
            } catch (e: Exception) {
                true
            }
        }
    }
}
