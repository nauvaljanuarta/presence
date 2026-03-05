const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");

admin.initializeApp();
const db = admin.firestore();

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

// ========================
// POST /api/presence/qr/generate
// ========================
app.post("/presence/qr/generate", async (req, res) => {
    const { course_id, session_id, timestamp } = req.body;

    if (!course_id || !session_id || !timestamp) {
        return res.json({ ok: false, error: "missing_field" });
    }

    const qrToken =
        "TKN-" +
        Math.random()
            .toString(36)
            .substring(2, 8)
            .toUpperCase();

    const now = new Date();
    const expires_at = new Date(now.getTime() + 30000); // 30 detik

    await db.collection("tokens").add({
        qr_token: qrToken,
        session_id,
        course_id,
        expires_at: admin.firestore.Timestamp.fromDate(expires_at),
        created_at: admin.firestore.Timestamp.fromDate(
            timestamp ? new Date(timestamp) : now
        ),
    });

    return res.json({
        ok: true,
        data: {
            qr_token: qrToken,
            session_id,
            course_id,
            expires_at: expires_at.toISOString(),
        },
    });
});

// ========================
// POST /api/presence/checkin
// ========================
app.post("/presence/checkin", async (req, res) => {
    const { user_id, device_id, qr_token, timestamp } = req.body;

    if (!user_id || !device_id || !qr_token || !timestamp) {
        return res.json({ ok: false, error: "missing_field" });
    }

    // Cari token di Firestore
    const tokenSnap = await db
        .collection("tokens")
        .where("qr_token", "==", qr_token)
        .limit(1)
        .get();

    if (tokenSnap.empty) {
        return res.json({ ok: false, error: "token_invalid" });
    }

    const tokenData = tokenSnap.docs[0].data();
    const expiresAt = tokenData.expires_at.toDate();
    const now = new Date();

    if (now > expiresAt) {
        return res.json({ ok: false, error: "token_expired" });
    }

    const course_id = tokenData.course_id;
    const session_id = tokenData.session_id;

    // Cek apakah sudah check-in
    const existingSnap = await db
        .collection("presences")
        .where("user_id", "==", user_id)
        .where("course_id", "==", course_id)
        .where("session_id", "==", session_id)
        .limit(1)
        .get();

    if (!existingSnap.empty) {
        return res.json({ ok: false, error: "already_checked_in" });
    }

    const presenceId =
        "HDR-" +
        Math.random()
            .toString(36)
            .substring(2, 10);

    await db.collection("presences").add({
        presence_id: presenceId,
        user_id,
        device_id,
        course_id,
        session_id,
        qr_token,
        timestamp: admin.firestore.Timestamp.fromDate(new Date(timestamp)),
    });

    return res.json({
        ok: true,
        data: {
            presence_id: presenceId,
            course_id,
            session_id,
            status: "checked_in",
        },
    });
});

// ========================
// GET /api/presence/status
// ========================
app.get("/presence/status", async (req, res) => {
    const { user_id, course_id, session_id } = req.query;

    if (!user_id || !course_id || !session_id) {
        return res.json({ ok: false, error: "missing_field" });
    }

    const snap = await db
        .collection("presences")
        .where("user_id", "==", user_id)
        .where("course_id", "==", course_id)
        .where("session_id", "==", session_id)
        .limit(1)
        .get();

    if (!snap.empty) {
        const data = snap.docs[0].data();
        return res.json({
            ok: true,
            data: {
                user_id,
                course_id,
                session_id,
                status: "checked_in",
                last_timestamp: data.timestamp.toDate().toISOString(),
            },
        });
    }

    return res.json({
        ok: true,
        data: {
            user_id,
            course_id,
            session_id,
            status: "not_checked_in",
        },
    });
});

// Export sebagai Firebase Cloud Function
exports.api = functions.https.onRequest(app);
