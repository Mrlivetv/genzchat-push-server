const express = require("express");
const admin = require("firebase-admin");

// The service account JSON is stored as an environment variable
// (set in Render dashboard) so it's never committed to GitHub.
const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT_JSON);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const app = express();
app.use(express.json());

// Simple health check
app.get("/", (req, res) => {
  res.send("GenZChat push server is running. Dev: Mostak");
});

// This matches the exact request shape lib/notification_service.dart already sends
app.post("/api/cloud/messaging", async (req, res) => {
  try {
    const {
      receiverFcmToken,
      senderName,
      messageText,
      conversationId,
      senderId,
      messageId,
      type,
      callChannelId,
    } = req.body;

    if (!receiverFcmToken) {
      return res.status(400).json({ error: "receiverFcmToken is required" });
    }

    const message = {
      token: receiverFcmToken,
      data: {
        senderName: senderName || "",
        text: messageText || "",
        conversationId: conversationId || "",
        senderId: senderId || "",
        messageId: messageId || "",
        type: type || "message",
        callChannelId: callChannelId || "",
      },
      android: {
        priority: "high",
      },
    };

    const response = await admin.messaging().send(message);
    return res.status(200).json({ success: true, messageId: response });
  } catch (err) {
    console.error("Push send failed:", err);
    return res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`GenZChat push server listening on ${PORT}`));
