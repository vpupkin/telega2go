"""Funny Telegram Bot Commands for OTP Social Gateway"""
import random
import asyncio
from datetime import datetime, timezone
from typing import Dict, List
import httpx

class FunnyBotCommands:
    """Collection of funny and useful Telegram bot commands"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.telegram_api_base = f"https://api.telegram.org/bot{bot_token}"
        
        # Funny responses and jokes
        self.funny_responses = {
            "start": [
                "🎉 Welcome to the OTP Social Gateway! I'm your digital security guard with a sense of humor!",
                "🔐 Hey there! I'm the bot that sends OTPs so secure, even I can't remember them!",
                "🚀 Welcome! I'm here to send you codes that disappear faster than your motivation on Monday!",
                "💫 Greetings! I'm the OTP bot that's more reliable than your alarm clock!"
            ],
            "help": [
                "🤖 I'm your OTP delivery bot! Here's what I can do:\n\n"
                "🔐 /otp - Send a secure OTP (if you're authorized)\n"
                "😄 /joke - Get a random joke to brighten your day\n"
                "🎲 /dice - Roll some dice for decision making\n"
                "🔮 /fortune - Get your daily fortune\n"
                "📊 /stats - Check my delivery statistics\n"
                "🎭 /mood - Check my current mood\n"
                "🆘 /panic - Emergency mode (just kidding, I'm always calm)\n"
                "❓ /help - Show this help message\n\n"
                "Remember: I'm more secure than your ex's password! 🔒",
                
                "🛡️ I'm your digital security companion! Available commands:\n\n"
                "🔐 /otp - Request an OTP (authorized users only)\n"
                "😂 /joke - Laugh your way through security\n"
                "🎲 /dice - Let fate decide for you\n"
                "🔮 /fortune - Peek into the future\n"
                "📈 /stats - See how busy I've been\n"
                "😊 /mood - Check if I'm having a good day\n"
                "🚨 /panic - Activate emergency protocols (not really)\n"
                "❓ /help - This helpful message\n\n"
                "I'm so secure, even I don't know my own secrets! 🤐"
            ],
            "joke": [
                "Why don't OTPs ever get lonely? Because they always come in pairs! 🔐💕",
                "What do you call an OTP that's always late? A delayed-time password! ⏰😅",
                "Why did the OTP break up with the password? It needed some space! 💔",
                "What's an OTP's favorite music? One-time hits! 🎵",
                "Why don't OTPs play hide and seek? Because they always expire before you find them! 🕵️‍♂️",
                "What do you call a nervous OTP? A shaky-time password! 😰",
                "Why did the OTP go to therapy? It had too many trust issues! 🛋️",
                "What's an OTP's favorite sport? Password tennis! 🎾",
                "Why don't OTPs ever get cold? Because they're always hot! 🔥",
                "What do you call an OTP that tells jokes? A funny-time password! 😂"
            ],
            "fortune": [
                "🔮 Your fortune: You will receive an OTP today that actually works on the first try! ✨",
                "🔮 Your fortune: A secure connection is in your future... and it's not your ex! 💫",
                "🔮 Your fortune: You will remember a password without having to reset it! 🎯",
                "🔮 Your fortune: Your two-factor authentication will be as strong as your coffee! ☕",
                "🔮 Your fortune: You will never again use 'password123' as your password! 🚫",
                "🔮 Your fortune: A mysterious stranger will send you a secure message... it's me! 👻",
                "🔮 Your fortune: Your digital security will be tighter than your budget! 💰",
                "🔮 Your fortune: You will discover a new password that you can actually remember! 🧠",
                "🔮 Your fortune: Your OTP will arrive faster than your pizza delivery! 🍕",
                "🔮 Your fortune: You will achieve the impossible: remembering all your passwords! 🏆"
            ],
            "mood": [
                "😊 I'm feeling great! Just sent 42 OTPs today and they all worked perfectly!",
                "🤖 I'm in a fantastic mood! My circuits are buzzing with security energy!",
                "💪 I'm feeling powerful! Ready to protect your digital life!",
                "🎉 I'm ecstatic! Another day of keeping hackers at bay!",
                "😎 I'm cool as a cucumber! Security is my middle name!",
                "🚀 I'm soaring high! Ready to deliver OTPs at the speed of light!",
                "🌟 I'm shining bright! Your digital guardian angel is here!",
                "🔥 I'm on fire! Burning through security threats like they're nothing!",
                "💎 I'm feeling precious! Like the security gem I am!",
                "🎭 I'm in a dramatic mood! Ready to perform the greatest security show ever!"
            ],
            "panic": [
                "🚨 PANIC MODE ACTIVATED! Just kidding, I'm always calm! 😌",
                "🚨 EMERGENCY PROTOCOLS ENGAGED! Actually, I'm just here to send OTPs! 🤖",
                "🚨 ALERT! ALERT! I'm having a panic attack... about how secure you are! 🔒",
                "🚨 CODE RED! Just kidding, everything is green and secure! 🟢",
                "🚨 EMERGENCY! I need to send you an OTP immediately! Wait, that's my job! 😅",
                "🚨 PANIC! PANIC! I can't find my sense of humor... oh wait, here it is! 😂",
                "🚨 ALERT! I'm panicking about how much I love sending secure messages! 💕",
                "🚨 EMERGENCY! I need to tell you a joke right now! Why did the OTP cross the road? To get to the other secure side! 🐔",
                "🚨 PANIC MODE! I'm so excited about security that I can't contain myself! 🎉",
                "🚨 ALERT! I'm having an existential crisis... about which emoji to use next! 🤔"
            ]
        }
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Send a message to a Telegram chat"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.telegram_api_base}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    }
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    async def handle_command(self, chat_id: str, command: str, username: str = None) -> bool:
        """Handle incoming bot commands"""
        command = command.lower().strip()
        
        if command == "/start":
            message = random.choice(self.funny_responses["start"])
            if username:
                message = f"Hey @{username}! {message}"
            return await self.send_message(chat_id, message)
        
        elif command == "/help":
            message = random.choice(self.funny_responses["help"])
            return await self.send_message(chat_id, message)
        
        elif command == "/joke":
            message = random.choice(self.funny_responses["joke"])
            return await self.send_message(chat_id, message)
        
        elif command == "/dice":
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            total = dice1 + dice2
            
            messages = [
                f"🎲 Rolling the dice...\n\n🎯 First die: {dice1}\n🎯 Second die: {dice2}\n\n🎊 Total: {total}",
                f"🎲 *shakes dice vigorously*\n\n🎯 {dice1} + {dice2} = {total}\n\n{'🎉 Lucky roll!' if total >= 10 else '😅 Better luck next time!'}",
                f"🎲 The dice have spoken!\n\n🎯 {dice1} and {dice2}\n\n🎊 Sum: {total}\n\n{'🌟 Excellent!' if total >= 11 else '😊 Not bad!' if total >= 7 else '🤷‍♂️ Could be worse!'}"
            ]
            message = random.choice(messages)
            return await self.send_message(chat_id, message)
        
        elif command == "/fortune":
            message = random.choice(self.funny_responses["fortune"])
            return await self.send_message(chat_id, message)
        
        elif command == "/stats":
            # Mock stats for now - in real implementation, get from actual data
            stats = {
                "otps_sent": random.randint(100, 999),
                "success_rate": random.randint(95, 100),
                "uptime": "99.9%",
                "mood": random.choice(["😊", "🤖", "💪", "🎉", "😎"])
            }
            
            message = f"""📊 <b>OTP Social Gateway Statistics</b>

🔐 OTPs Sent Today: {stats['otps_sent']}
✅ Success Rate: {stats['success_rate']}%
⏰ Uptime: {stats['uptime']}
😊 My Mood: {stats['mood']}

<i>I'm working harder than a password on a Monday morning!</i>"""
            return await self.send_message(chat_id, message)
        
        elif command == "/mood":
            message = random.choice(self.funny_responses["mood"])
            return await self.send_message(chat_id, message)
        
        elif command == "/panic":
            message = random.choice(self.funny_responses["panic"])
            return await self.send_message(chat_id, message)
        
        elif command == "/otp":
            message = """🔐 <b>OTP Request</b>

I can't send OTPs directly through commands for security reasons! 

To get an OTP, you need to:
1. Go to the registration system
2. Complete the proper authentication flow
3. I'll send you a secure OTP with QR code!

<i>Security first, jokes second! 😄🔒</i>"""
            return await self.send_message(chat_id, message)
        
        else:
            message = f"""❓ <b>Unknown Command</b>

I don't recognize '{command}'. 

Try one of these:
/help - See all commands
/joke - Get a laugh
/dice - Roll some dice
/fortune - Get your fortune
/stats - Check my stats
/mood - Check my mood

<i>I'm helpful, not mind-reading! 🤖</i>"""
            return await self.send_message(chat_id, message)
    
    async def send_welcome_message(self, chat_id: str, username: str = None) -> bool:
        """Send a welcome message when someone starts chatting"""
        welcome_messages = [
            f"🎉 Hey there{' @' + username if username else ''}! Welcome to the most secure bot on Telegram!",
            f"🔐 {'@' + username + ', ' if username else ''}you've found the OTP master! Ready to secure your digital life?",
            f"🚀 {'@' + username + ', ' if username else ''}welcome to the future of security! I'm your digital guardian!",
            f"💫 {'@' + username + ', ' if username else ''}you're now chatting with the most reliable bot in the universe!"
        ]
        
        message = random.choice(welcome_messages)
        message += "\n\nType /help to see what I can do! 😊"
        
        return await self.send_message(chat_id, message)
