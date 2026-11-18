{
echo "== host"; hostname; uptime; sw_vers -productVersion
echo "== service"; launchctl print gui/501/com.chatbot.bridge 2>&1 | grep -E "state|pid|last exit|runs"
echo "== processes"; ps aux | grep -E "dist/index|whatsapp-sidecar" | grep -v grep
echo "== dist checksums (first 16 chars)"; cd /Users/ptpakdefarma/chatbot/bridge/dist && shasum -a 256 core/router.js channels/telegram.js core/llm-client.js index.js | cut -c1-16,65-
echo "== dist timestamps"; ls -la core/router.js channels/telegram.js
echo "== data dir"; ls -la /Users/ptpakdefarma/chatbot/bridge/data | tail -n 25
echo "== tailscale on the Mac"; (tailscale status 2>&1 || /Applications/Tailscale.app/Contents/MacOS/Tailscale status 2>&1) | head -n 8
echo "== sshd"; sudo -n systemsetup -getremotelogin 2>&1 | head -n 2
echo "== log tail"; tail -n 80 /Users/ptpakdefarma/chatbot/logs/bridge.log
} 2>&1 | sed -E 's/bot[0-9]+:[A-Za-z0-9_-]+/bot<REDACTED>/g; s/sk-[A-Za-z0-9]{8,}/sk-<REDACTED>/g'
