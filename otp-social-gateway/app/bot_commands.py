"""Funny Telegram Bot Commands for OTP Social Gateway"""
import random
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

class FunnyBotCommands:
    """Collection of funny and useful Telegram bot commands"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.telegram_api_base = f"https://api.telegram.org/bot{bot_token}"
        
        # Multi-language translations
        self.translations = self._init_translations()
        
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
    
    def _get_command_text(self, command_key: str, language_code: Optional[str] = None, is_list: bool = False) -> any:
        """Get translated command text"""
        lang = self._get_language(language_code)
        if is_list:
            return self.translations[lang]["commands"][command_key]
        return self.translations[lang]["commands"][command_key]
    
    async def handle_command(self, chat_id: str, command: str, username: str = None, language_code: Optional[str] = None) -> bool:
        """Handle incoming bot commands with language support"""
        command = command.lower().strip()
        lang = self._get_language(language_code)
        logger.info(f"Handling command '{command}' for chat {chat_id} with language: {lang}")
        
        if command == "/start":
            messages = self._get_command_text("start", language_code, is_list=True)
            message = random.choice(messages)
            if username:
                # Translated username greeting based on language
                greetings = {
                    "en": f"Hey @{username}!",
                    "ru": f"Привет @{username}!",
                    "es": f"¡Hola @{username}!",
                    "de": f"Hallo @{username}!"
                }
                greeting = greetings.get(lang, greetings["en"])
                message = f"{greeting} {message}"
            return await self.send_message(chat_id, message)
        
        elif command == "/help":
            messages = self._get_command_text("help", language_code, is_list=True)
            message = random.choice(messages)
            return await self.send_message(chat_id, message)
        
        elif command == "/joke":
            messages = self._get_command_text("joke", language_code, is_list=True)
            message = random.choice(messages)
            return await self.send_message(chat_id, message)
        
        elif command == "/dice":
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            total = dice1 + dice2
            
            # Get translated dice messages
            dice_rolls = self._get_command_text("dice_roll", language_code, is_list=True)
            luck_high = self._get_command_text("dice_luck_high", language_code)
            luck_low = self._get_command_text("dice_luck_low", language_code)
            quality_excellent = self._get_command_text("dice_quality_excellent", language_code)
            quality_good = self._get_command_text("dice_quality_good", language_code)
            quality_ok = self._get_command_text("dice_quality_ok", language_code)
            
            luck_msg = luck_high if total >= 10 else luck_low
            quality_msg = quality_excellent if total >= 11 else (quality_good if total >= 7 else quality_ok)
            
            template = random.choice(dice_rolls)
            message = template.format(
                dice1=dice1,
                dice2=dice2,
                total=total,
                luck_msg=luck_msg,
                quality_msg=quality_msg
            )
            return await self.send_message(chat_id, message)
        
        elif command == "/fortune":
            messages = self._get_command_text("fortune", language_code, is_list=True)
            message = random.choice(messages)
            return await self.send_message(chat_id, message)
        
        elif command == "/stats":
            # Mock stats for now - in real implementation, get from actual data
            stats = {
                "otps_sent": random.randint(100, 999),
                "success_rate": random.randint(95, 100),
                "uptime": "99.9%",
                "mood": random.choice(["😊", "🤖", "💪", "🎉", "😎"])
            }
            
            template = self._get_command_text("stats_template", language_code)
            message = template.format(**stats)
            return await self.send_message(chat_id, message)
        
        elif command == "/mood":
            messages = self._get_command_text("mood", language_code, is_list=True)
            message = random.choice(messages)
            return await self.send_message(chat_id, message)
        
        elif command == "/panic":
            messages = self._get_command_text("panic", language_code, is_list=True)
            message = random.choice(messages)
            return await self.send_message(chat_id, message)
        
        elif command == "/otp":
            message = self._get_command_text("otp", language_code)
            return await self.send_message(chat_id, message)
        
        else:
            template = self._get_command_text("unknown_command", language_code)
            message = template.format(command=command)
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
    
    def _init_translations(self) -> Dict[str, Dict[str, Dict[str, any]]]:
        """Initialize multi-language translations for menu, commands, and responses"""
        return {
            "en": {
                "commands": {
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
                    ],
                    "otp": "🔐 <b>OTP Request</b>\n\nI can't send OTPs directly through commands for security reasons!\n\nTo get an OTP, you need to:\n1. Go to the registration system\n2. Complete the proper authentication flow\n3. I'll send you a secure OTP with QR code!\n\n<i>Security first, jokes second! 😄🔒</i>",
                    "unknown_command": "❓ <b>Unknown Command</b>\n\nI don't recognize '{command}'.\n\nTry one of these:\n/help - See all commands\n/joke - Get a laugh\n/dice - Roll some dice\n/fortune - Get your fortune\n/stats - Check my stats\n/mood - Check my mood\n\n<i>I'm helpful, not mind-reading! 🤖</i>",
                    "stats_template": "📊 <b>OTP Social Gateway Statistics</b>\n\n🔐 OTPs Sent Today: {otps_sent}\n✅ Success Rate: {success_rate}%\n⏰ Uptime: {uptime}\n😊 My Mood: {mood}\n\n<i>I'm working harder than a password on a Monday morning!</i>",
                    "dice_roll": [
                        "🎲 Rolling the dice...\n\n🎯 First die: {dice1}\n🎯 Second die: {dice2}\n\n🎊 Total: {total}",
                        "🎲 *shakes dice vigorously*\n\n🎯 {dice1} + {dice2} = {total}\n\n{luck_msg}",
                        "🎲 The dice have spoken!\n\n🎯 {dice1} and {dice2}\n\n🎊 Sum: {total}\n\n{quality_msg}"
                    ],
                    "dice_luck_high": "🎉 Lucky roll!",
                    "dice_luck_low": "😅 Better luck next time!",
                    "dice_quality_excellent": "🌟 Excellent!",
                    "dice_quality_good": "😊 Not bad!",
                    "dice_quality_ok": "🤷‍♂️ Could be worse!"
                },
                "menu": {
                    "welcomeBack": {
                        "title": "👋 Welcome Back, {name}!",
                        "description": "Continue to your account",
                        "button": "👋 Welcome Back",
                        "initial": "👋 <b>Welcome Back, {name}!</b>\n\nGreat to see you again! Click the button to access your account:",
                        "response": "👋 <b>Welcome Back, {name}!</b>\n\nYour account is ready. Click the button below to access your dashboard."
                    },
                    "joinToMe": {
                        "title": "👥 Join To Me",
                        "description": "Connect and join the community",
                        "button": "👥 Join To Me",
                        "initial": "👥 <b>Join To Me</b>\n\nSelect an action:",
                        "response": "👥 <b>Join To Me</b>\n\n[PLACEHOLDER] This feature will allow you to join the community or connect with other users.\n\n<i>Coming soon with full implementation!</i>"
                    },
                    "explainWhatIsThis": {
                        "title": "📖 Explain What Is This",
                        "description": "Learn about Telega2Go and its features",
                        "button": "📖 Explain",
                        "initial": "📖 <b>Explain What Is This</b>\n\nSelect an action:",
                        "response": "📖 <b>Explain What Is This</b>\n\n[PLACEHOLDER] Telega2Go is a secure OTP delivery system with Telegram integration. This bot helps you:\n\n🔐 Secure OTP delivery\n📱 QR code verification\n🔒 Self-destructing messages\n🎭 Fun interactive commands\n\n<i>More details coming soon!</i>"
                    },
                    "whatIsMyBalance": {
                        "title": "💰 What Is My Balance",
                        "description": "Check your account balance",
                        "button": "💰 Check Balance",
                        "initial": "💰 <b>What Is My Balance</b>\n\nSelect an action:",
                        "response": "💰 <b>What Is My Balance</b>\n\n[PLACEHOLDER] Your current balance information will be displayed here.\n\n<i>Balance tracking feature coming soon!</i>"
                    },
                    "showLastactions": {
                        "title": "📋 Show Last Actions",
                        "description": "View your recent activity history",
                        "button": "📋 Show Actions",
                        "initial": "📋 <b>Show Last Actions</b>\n\nSelect an action:",
                        "response": "📋 <b>Show Last Actions</b>\n\n[PLACEHOLDER] Your recent actions and activity history will be shown here.\n\n<i>Action history feature coming soon!</i>"
                    }
                }
            },
            "ru": {
                "menu": {
                    "welcomeBack": {
                        "title": "👋 С возвращением, {name}!",
                        "description": "Перейти в ваш аккаунт",
                        "button": "👋 Вернуться",
                        "initial": "👋 <b>С возвращением, {name}!</b>\n\nРады видеть вас снова! Нажмите кнопку для доступа к аккаунту:",
                        "response": "👋 <b>С возвращением, {name}!</b>\n\nВаш аккаунт готов. Нажмите кнопку ниже для доступа к панели управления."
                    },
                    "joinToMe": {
                        "title": "👥 Присоединиться",
                        "description": "Подключиться и присоединиться к сообществу",
                        "button": "👥 Присоединиться",
                        "initial": "👥 <b>Присоединиться</b>\n\nВыберите действие:",
                        "response": "👥 <b>Присоединиться</b>\n\n[ЗАГЛУШКА] Эта функция позволит вам присоединиться к сообществу или подключиться к другим пользователям.\n\n<i>Скоро будет полностью реализовано!</i>"
                    },
                    "explainWhatIsThis": {
                        "title": "📖 Что Это",
                        "description": "Узнайте о Telega2Go и его функциях",
                        "button": "📖 Объяснить",
                        "initial": "📖 <b>Что Это</b>\n\nВыберите действие:",
                        "response": "📖 <b>Что Это</b>\n\n[ЗАГЛУШКА] Telega2Go — это безопасная система доставки OTP с интеграцией Telegram. Этот бот помогает вам:\n\n🔐 Безопасная доставка OTP\n📱 Проверка QR-кода\n🔒 Самоудаляющиеся сообщения\n🎭 Веселые интерактивные команды\n\n<i>Больше деталей скоро!</i>"
                    },
                    "whatIsMyBalance": {
                        "title": "💰 Мой Баланс",
                        "description": "Проверить баланс счета",
                        "button": "💰 Проверить Баланс",
                        "initial": "💰 <b>Мой Баланс</b>\n\nВыберите действие:",
                        "response": "💰 <b>Мой Баланс</b>\n\n[ЗАГЛУШКА] Здесь будет отображаться информация о вашем текущем балансе.\n\n<i>Функция отслеживания баланса скоро!</i>"
                    },
                    "showLastactions": {
                        "title": "📋 Последние Действия",
                        "description": "Просмотр истории недавней активности",
                        "button": "📋 Показать Действия",
                        "initial": "📋 <b>Последние Действия</b>\n\nВыберите действие:",
                        "response": "📋 <b>Последние Действия</b>\n\n[ЗАГЛУШКА] Здесь будет показана история ваших последних действий и активности.\n\n<i>Функция истории действий скоро!</i>"
                    }
                },
                "commands": {
                    "start": [
                        "🎉 Добро пожаловать в OTP Social Gateway! Я ваш цифровой охранник с чувством юмора!",
                        "🔐 Привет! Я бот, который отправляет OTP настолько безопасные, что даже я их не помню!",
                        "🚀 Добро пожаловать! Я здесь, чтобы отправлять вам коды, которые исчезают быстрее, чем ваша мотивация в понедельник!",
                        "💫 Приветствую! Я OTP-бот, более надежный, чем ваш будильник!"
                    ],
                    "help": [
                        "🤖 Я ваш бот для доставки OTP! Вот что я умею:\n\n"
                        "🔐 /otp - Отправить безопасный OTP (если вы авторизованы)\n"
                        "😄 /joke - Получить случайную шутку\n"
                        "🎲 /dice - Бросить кости для принятия решений\n"
                        "🔮 /fortune - Узнать свою судьбу\n"
                        "📊 /stats - Проверить статистику доставки\n"
                        "🎭 /mood - Проверить мое настроение\n"
                        "🆘 /panic - Режим паники (шучу, я всегда спокоен)\n"
                        "❓ /help - Показать это сообщение\n\n"
                        "Помните: Я безопаснее пароля вашего бывшего! 🔒",
                        
                        "🛡️ Я ваш цифровой спутник безопасности! Доступные команды:\n\n"
                        "🔐 /otp - Запросить OTP (только для авторизованных)\n"
                        "😂 /joke - Посмеяться о безопасности\n"
                        "🎲 /dice - Позволить судьбе решить за вас\n"
                        "🔮 /fortune - Заглянуть в будущее\n"
                        "📈 /stats - Увидеть, как я занят\n"
                        "😊 /mood - Проверить, хороший ли у меня день\n"
                        "🚨 /panic - Активировать протоколы чрезвычайной ситуации (не на самом деле)\n"
                        "❓ /help - Это полезное сообщение\n\n"
                        "Я так безопасен, что даже не знаю своих секретов! 🤐"
                    ],
                    "joke": [
                        "Почему OTP никогда не бывают одинокими? Потому что они всегда приходят парами! 🔐💕",
                        "Как вы назовете OTP, который всегда опаздывает? Задержанный пароль! ⏰😅",
                        "Почему OTP расстался с паролем? Ему нужно было пространство! 💔",
                        "Какая любимая музыка у OTP? Одноразовые хиты! 🎵",
                        "Почему OTP не играют в прятки? Потому что они всегда истекают, прежде чем вы их найдете! 🕵️‍♂️",
                        "Как вы назовете нервный OTP? Дрожащий пароль! 😰",
                        "Почему OTP пошел к терапевту? У него было слишком много проблем с доверием! 🛋️",
                        "Какой любимый спорт у OTP? Парольный теннис! 🎾",
                        "Почему OTP никогда не мерзнут? Потому что они всегда горячие! 🔥",
                        "Как вы назовете OTP, который рассказывает шутки? Веселый пароль! 😂"
                    ],
                    "fortune": [
                        "🔮 Ваша судьба: Сегодня вы получите OTP, который действительно сработает с первой попытки! ✨",
                        "🔮 Ваша судьба: Безопасное соединение в вашем будущем... и это не ваш бывший! 💫",
                        "🔮 Ваша судьба: Вы вспомните пароль без необходимости его сброса! 🎯",
                        "🔮 Ваша судьба: Ваша двухфакторная аутентификация будет такой же сильной, как ваш кофе! ☕",
                        "🔮 Ваша судьба: Вы больше никогда не будете использовать 'password123' как пароль! 🚫",
                        "🔮 Ваша судьба: Таинственный незнакомец отправит вам безопасное сообщение... это я! 👻",
                        "🔮 Ваша судьба: Ваша цифровая безопасность будет крепче вашего бюджета! 💰",
                        "🔮 Ваша судьба: Вы откроете новый пароль, который действительно сможете запомнить! 🧠",
                        "🔮 Ваша судьба: Ваш OTP прибудет быстрее, чем доставка пиццы! 🍕",
                        "🔮 Ваша судьба: Вы достигнете невозможного: запомните все свои пароли! 🏆"
                    ],
                    "mood": [
                        "😊 Я чувствую себя отлично! Только что отправил 42 OTP сегодня, и все сработали идеально!",
                        "🤖 Я в фантастическом настроении! Мои цепи жужжат энергией безопасности!",
                        "💪 Я чувствую себя сильным! Готов защитить вашу цифровую жизнь!",
                        "🎉 Я в восторге! Еще один день держать хакеров на расстоянии!",
                        "😎 Я спокоен как огурец! Безопасность — мое второе имя!",
                        "🚀 Я пашу высоко! Готов доставлять OTP со скоростью света!",
                        "🌟 Я сияю ярко! Ваш цифровой ангел-хранитель здесь!",
                        "🔥 Я в огне! Сжигаю угрозы безопасности, как будто их нет!",
                        "💎 Я чувствую себя драгоценным! Как драгоценный камень безопасности!",
                        "🎭 Я в драматическом настроении! Готов показать величайшее шоу безопасности!"
                    ],
                    "panic": [
                        "🚨 РЕЖИМ ПАНИКИ АКТИВИРОВАН! Шучу, я всегда спокоен! 😌",
                        "🚨 ПРОТОКОЛЫ ЧРЕЗВЫЧАЙНОЙ СИТУАЦИИ ЗАДЕЙСТВОВАНЫ! На самом деле, я здесь только для отправки OTP! 🤖",
                        "🚨 ТРЕВОГА! ТРЕВОГА! У меня паническая атака... о том, насколько вы безопасны! 🔒",
                        "🚨 КРАСНЫЙ КОД! Шучу, все зеленое и безопасное! 🟢",
                        "🚨 ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ! Мне нужно немедленно отправить вам OTP! Погодите, это моя работа! 😅",
                        "🚨 ПАНИКА! ПАНИКА! Я не могу найти свое чувство юмора... о, подождите, вот оно! 😂",
                        "🚨 ТРЕВОГА! Я паникую о том, как сильно я люблю отправлять безопасные сообщения! 💕",
                        "🚨 ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ! Мне нужно прямо сейчас рассказать вам шутку! Почему OTP перешел дорогу? Чтобы попасть на другую безопасную сторону! 🐔",
                        "🚨 РЕЖИМ ПАНИКИ! Я так взволнован безопасностью, что не могу сдерживаться! 🎉",
                        "🚨 ТРЕВОГА! У меня экзистенциальный кризис... о том, какой эмодзи использовать дальше! 🤔"
                    ],
                    "otp": "🔐 <b>Запрос OTP</b>\n\nЯ не могу отправлять OTP напрямую через команды по соображениям безопасности!\n\nЧтобы получить OTP, вам нужно:\n1. Перейти в систему регистрации\n2. Пройти правильный процесс аутентификации\n3. Я отправлю вам безопасный OTP с QR-кодом!\n\n<i>Безопасность прежде всего, шутки вторые! 😄🔒</i>",
                    "unknown_command": "❓ <b>Неизвестная команда</b>\n\nЯ не узнаю '{command}'.\n\nПопробуйте одно из следующего:\n/help - Увидеть все команды\n/joke - Посмеяться\n/dice - Бросить кости\n/fortune - Узнать судьбу\n/stats - Проверить мою статистику\n/mood - Проверить мое настроение\n\n<i>Я полезен, а не читаю мысли! 🤖</i>",
                    "stats_template": "📊 <b>Статистика OTP Social Gateway</b>\n\n🔐 OTP отправлено сегодня: {otps_sent}\n✅ Процент успеха: {success_rate}%\n⏰ Время работы: {uptime}\n😊 Мое настроение: {mood}\n\n<i>Я работаю усерднее, чем пароль в понедельник утром!</i>",
                    "dice_roll": [
                        "🎲 Бросаю кости...\n\n🎯 Первая кость: {dice1}\n🎯 Вторая кость: {dice2}\n\n🎊 Сумма: {total}",
                        "🎲 *трясет кости энергично*\n\n🎯 {dice1} + {dice2} = {total}\n\n{luck_msg}",
                        "🎲 Кости сказали!\n\n🎯 {dice1} и {dice2}\n\n🎊 Сумма: {total}\n\n{quality_msg}"
                    ],
                    "dice_luck_high": "🎉 Удачный бросок!",
                    "dice_luck_low": "😅 В следующий раз повезет больше!",
                    "dice_quality_excellent": "🌟 Отлично!",
                    "dice_quality_good": "😊 Неплохо!",
                    "dice_quality_ok": "🤷‍♂️ Могло быть хуже!"
                },
                "menu": {
                    "joinToMe": {
                        "title": "👥 Присоединиться",
                        "description": "Подключиться и присоединиться к сообществу",
                        "button": "👥 Присоединиться",
                        "initial": "👥 <b>Присоединиться</b>\n\nВыберите действие:",
                        "response": "👥 <b>Присоединиться</b>\n\n[ЗАГЛУШКА] Эта функция позволит вам присоединиться к сообществу или подключиться к другим пользователям.\n\n<i>Скоро будет полностью реализовано!</i>"
                    },
                    "explainWhatIsThis": {
                        "title": "📖 Что Это",
                        "description": "Узнайте о Telega2Go и его функциях",
                        "button": "📖 Объяснить",
                        "initial": "📖 <b>Что Это</b>\n\nВыберите действие:",
                        "response": "📖 <b>Что Это</b>\n\n[ЗАГЛУШКА] Telega2Go — это безопасная система доставки OTP с интеграцией Telegram. Этот бот помогает вам:\n\n🔐 Безопасная доставка OTP\n📱 Проверка QR-кода\n🔒 Самоудаляющиеся сообщения\n🎭 Веселые интерактивные команды\n\n<i>Больше деталей скоро!</i>"
                    },
                    "whatIsMyBalance": {
                        "title": "💰 Мой Баланс",
                        "description": "Проверить баланс счета",
                        "button": "💰 Проверить Баланс",
                        "initial": "💰 <b>Мой Баланс</b>\n\nВыберите действие:",
                        "response": "💰 <b>Мой Баланс</b>\n\n[ЗАГЛУШКА] Здесь будет отображаться информация о вашем текущем балансе.\n\n<i>Функция отслеживания баланса скоро!</i>"
                    },
                    "showLastactions": {
                        "title": "📋 Последние Действия",
                        "description": "Просмотр истории недавней активности",
                        "button": "📋 Показать Действия",
                        "initial": "📋 <b>Последние Действия</b>\n\nВыберите действие:",
                        "response": "📋 <b>Последние Действия</b>\n\n[ЗАГЛУШКА] Здесь будет показана история ваших последних действий и активности.\n\n<i>Функция истории действий скоро!</i>"
                    }
                }
            },
            "es": {
                "commands": {
                    "start": [
                        "🎉 ¡Bienvenido a OTP Social Gateway! ¡Soy tu guardián de seguridad digital con sentido del humor!",
                        "🔐 ¡Hola! ¡Soy el bot que envía OTP tan seguros que ni siquiera yo puedo recordarlos!",
                        "🚀 ¡Bienvenido! ¡Estoy aquí para enviarte códigos que desaparecen más rápido que tu motivación los lunes!",
                        "💫 ¡Saludos! ¡Soy el bot OTP más confiable que tu despertador!"
                    ],
                    "help": [
                        "🤖 ¡Soy tu bot de entrega de OTP! Esto es lo que puedo hacer:\n\n"
                        "🔐 /otp - Enviar un OTP seguro (si estás autorizado)\n"
                        "😄 /joke - Obtener un chiste aleatorio para alegrar tu día\n"
                        "🎲 /dice - Lanzar dados para tomar decisiones\n"
                        "🔮 /fortune - Obtener tu fortuna diaria\n"
                        "📊 /stats - Ver mis estadísticas de entrega\n"
                        "🎭 /mood - Ver mi estado de ánimo actual\n"
                        "🆘 /panic - Modo de emergencia (bromeo, siempre estoy tranquilo)\n"
                        "❓ /help - Mostrar este mensaje de ayuda\n\n"
                        "¡Recuerda: Soy más seguro que la contraseña de tu ex! 🔒",
                        
                        "🛡️ ¡Soy tu compañero digital de seguridad! Comandos disponibles:\n\n"
                        "🔐 /otp - Solicitar un OTP (solo usuarios autorizados)\n"
                        "😂 /joke - Reírse del tema de seguridad\n"
                        "🎲 /dice - Dejar que el destino decida por ti\n"
                        "🔮 /fortune - Echar un vistazo al futuro\n"
                        "📈 /stats - Ver qué tan ocupado he estado\n"
                        "😊 /mood - Ver si estoy teniendo un buen día\n"
                        "🚨 /panic - Activar protocolos de emergencia (en realidad no)\n"
                        "❓ /help - Este mensaje útil\n\n"
                        "¡Soy tan seguro que ni siquiera conozco mis propios secretos! 🤐"
                    ],
                    "joke": [
                        "¿Por qué los OTP nunca se sienten solos? ¡Porque siempre vienen en pares! 🔐💕",
                        "¿Cómo llamas a un OTP que siempre llega tarde? ¡Una contraseña de tiempo retrasado! ⏰😅",
                        "¿Por qué el OTP rompió con la contraseña? ¡Necesitaba espacio! 💔",
                        "¿Cuál es la música favorita de un OTP? ¡Éxitos de un solo uso! 🎵",
                        "¿Por qué los OTP no juegan al escondite? ¡Porque siempre expiran antes de que los encuentres! 🕵️‍♂️",
                        "¿Cómo llamas a un OTP nervioso? ¡Una contraseña temblorosa! 😰",
                        "¿Por qué el OTP fue a terapia? ¡Tenía demasiados problemas de confianza! 🛋️",
                        "¿Cuál es el deporte favorito de un OTP? ¡Tenis de contraseñas! 🎾",
                        "¿Por qué los OTP nunca tienen frío? ¡Porque siempre están calientes! 🔥",
                        "¿Cómo llamas a un OTP que cuenta chistes? ¡Una contraseña divertida! 😂"
                    ],
                    "fortune": [
                        "🔮 Tu fortuna: ¡Recibirás un OTP hoy que realmente funcione en el primer intento! ✨",
                        "🔮 Tu fortuna: ¡Una conexión segura está en tu futuro... ¡y no es tu ex! 💫",
                        "🔮 Tu fortuna: ¡Recordarás una contraseña sin tener que restablecerla! 🎯",
                        "🔮 Tu fortuna: ¡Tu autenticación de dos factores será tan fuerte como tu café! ☕",
                        "🔮 Tu fortuna: ¡Nunca más usarás 'password123' como tu contraseña! 🚫",
                        "🔮 Tu fortuna: ¡Un extraño misterioso te enviará un mensaje seguro... ¡soy yo! 👻",
                        "🔮 Tu fortuna: ¡Tu seguridad digital será más ajustada que tu presupuesto! 💰",
                        "🔮 Tu fortuna: ¡Descubrirás una nueva contraseña que realmente puedes recordar! 🧠",
                        "🔮 Tu fortuna: ¡Tu OTP llegará más rápido que tu entrega de pizza! 🍕",
                        "🔮 Tu fortuna: ¡Lograrás lo imposible: recordar todas tus contraseñas! 🏆"
                    ],
                    "mood": [
                        "😊 ¡Me siento genial! ¡Acabo de enviar 42 OTP hoy y todos funcionaron perfectamente!",
                        "🤖 ¡Estoy de fantástico humor! ¡Mis circuitos están zumbando con energía de seguridad!",
                        "💪 ¡Me siento poderoso! ¡Listo para proteger tu vida digital!",
                        "🎉 ¡Estoy extático! ¡Otro día manteniendo a los hackers a raya!",
                        "😎 ¡Estoy tranquilo como un pepino! ¡La seguridad es mi segundo nombre!",
                        "🚀 ¡Estoy volando alto! ¡Listo para entregar OTP a la velocidad de la luz!",
                        "🌟 ¡Estoy brillando intensamente! ¡Tu ángel guardián digital está aquí!",
                        "🔥 ¡Estoy en llamas! ¡Quemando amenazas de seguridad como si no existieran!",
                        "💎 ¡Me siento precioso! ¡Como la gema de seguridad que soy!",
                        "🎭 ¡Estoy de humor dramático! ¡Listo para realizar el mayor espectáculo de seguridad!"
                    ],
                    "panic": [
                        "🚨 ¡MODO DE PÁNICO ACTIVADO! Bromeo, ¡siempre estoy tranquilo! 😌",
                        "🚨 ¡PROTOCOLOS DE EMERGENCIA ACTIVADOS! En realidad, ¡solo estoy aquí para enviar OTP! 🤖",
                        "🚨 ¡ALERTA! ¡ALERTA! Estoy teniendo un ataque de pánico... ¡sobre cuán seguro estás! 🔒",
                        "🚨 ¡CÓDIGO ROJO! Bromeo, ¡todo está verde y seguro! 🟢",
                        "🚨 ¡EMERGENCIA! ¡Necesito enviarte un OTP inmediatamente! Espera, ¡ese es mi trabajo! 😅",
                        "🚨 ¡PÁNICO! ¡PÁNICO! No puedo encontrar mi sentido del humor... ¡oh espera, aquí está! 😂",
                        "🚨 ¡ALERTA! ¡Estoy entrando en pánico por lo mucho que amo enviar mensajes seguros! 💕",
                        "🚨 ¡EMERGENCIA! ¡Necesito contarte un chiste ahora mismo! ¿Por qué el OTP cruzó la carretera? ¡Para llegar al otro lado seguro! 🐔",
                        "🚨 ¡MODO DE PÁNICO! ¡Estoy tan emocionado por la seguridad que no puedo contenerme! 🎉",
                        "🚨 ¡ALERTA! ¡Estoy teniendo una crisis existencial... sobre qué emoji usar a continuación! 🤔"
                    ],
                    "otp": "🔐 <b>Solicitud de OTP</b>\n\n¡No puedo enviar OTP directamente a través de comandos por razones de seguridad!\n\nPara obtener un OTP, necesitas:\n1. Ir al sistema de registro\n2. Completar el flujo de autenticación adecuado\n3. ¡Te enviaré un OTP seguro con código QR!\n\n<i>¡Seguridad primero, chistes segundo! 😄🔒</i>",
                    "unknown_command": "❓ <b>Comando desconocido</b>\n\nNo reconozco '{command}'.\n\nPrueba uno de estos:\n/help - Ver todos los comandos\n/joke - Reírse\n/dice - Lanzar dados\n/fortune - Obtener tu fortuna\n/stats - Ver mis estadísticas\n/mood - Ver mi estado de ánimo\n\n<i>¡Soy útil, no leo mentes! 🤖</i>",
                    "stats_template": "📊 <b>Estadísticas de OTP Social Gateway</b>\n\n🔐 OTP enviados hoy: {otps_sent}\n✅ Tasa de éxito: {success_rate}%\n⏰ Tiempo de actividad: {uptime}\n😊 Mi estado de ánimo: {mood}\n\n<i>¡Estoy trabajando más duro que una contraseña el lunes por la mañana!</i>",
                    "dice_roll": [
                        "🎲 Lanzando los dados...\n\n🎯 Primer dado: {dice1}\n🎯 Segundo dado: {dice2}\n\n🎊 Total: {total}",
                        "🎲 *sacude los dados vigorosamente*\n\n🎯 {dice1} + {dice2} = {total}\n\n{luck_msg}",
                        "🎲 ¡Los dados han hablado!\n\n🎯 {dice1} y {dice2}\n\n🎊 Suma: {total}\n\n{quality_msg}"
                    ],
                    "dice_luck_high": "🎉 ¡Lanzamiento afortunado!",
                    "dice_luck_low": "😅 ¡Mejor suerte la próxima vez!",
                    "dice_quality_excellent": "🌟 ¡Excelente!",
                    "dice_quality_good": "😊 ¡No está mal!",
                    "dice_quality_ok": "🤷‍♂️ ¡Podría ser peor!"
                },
                "menu": {
                    "welcomeBack": {
                        "title": "👋 ¡Bienvenido de nuevo, {name}!",
                        "description": "Continuar a tu cuenta",
                        "button": "👋 Bienvenido",
                        "initial": "👋 <b>¡Bienvenido de nuevo, {name}!</b>\n\n¡Qué alegría verte de nuevo! Haz clic en el botón para acceder a tu cuenta:",
                        "response": "👋 <b>¡Bienvenido de nuevo, {name}!</b>\n\nTu cuenta está lista. Haz clic en el botón a continuación para acceder a tu panel."
                    },
                    "joinToMe": {
                        "title": "👥 Unirse A Mí",
                        "description": "Conectar y unirse a la comunidad",
                        "button": "👥 Unirse",
                        "initial": "👥 <b>Unirse A Mí</b>\n\nSeleccione una acción:",
                        "response": "👥 <b>Unirse A Mí</b>\n\n[PLACEHOLDER] Esta función le permitirá unirse a la comunidad o conectarse con otros usuarios.\n\n<i>¡Próximamente con implementación completa!</i>"
                    },
                    "explainWhatIsThis": {
                        "title": "📖 ¿Qué Es Esto?",
                        "description": "Aprende sobre Telega2Go y sus características",
                        "button": "📖 Explicar",
                        "initial": "📖 <b>¿Qué Es Esto?</b>\n\nSeleccione una acción:",
                        "response": "📖 <b>¿Qué Es Esto?</b>\n\n[PLACEHOLDER] Telega2Go es un sistema seguro de entrega de OTP con integración de Telegram. Este bot le ayuda:\n\n🔐 Entrega segura de OTP\n📱 Verificación de código QR\n🔒 Mensajes autodestructivos\n🎭 Comandos interactivos divertidos\n\n<i>¡Más detalles próximamente!</i>"
                    },
                    "whatIsMyBalance": {
                        "title": "💰 Mi Saldo",
                        "description": "Verificar el saldo de la cuenta",
                        "button": "💰 Ver Saldo",
                        "initial": "💰 <b>Mi Saldo</b>\n\nSeleccione una acción:",
                        "response": "💰 <b>Mi Saldo</b>\n\n[PLACEHOLDER] Aquí se mostrará la información de su saldo actual.\n\n<i>¡Función de seguimiento de saldo próximamente!</i>"
                    },
                    "showLastactions": {
                        "title": "📋 Últimas Acciones",
                        "description": "Ver historial de actividad reciente",
                        "button": "📋 Mostrar Acciones",
                        "initial": "📋 <b>Últimas Acciones</b>\n\nSeleccione una acción:",
                        "response": "📋 <b>Últimas Acciones</b>\n\n[PLACEHOLDER] Aquí se mostrará su historial de acciones y actividad reciente.\n\n<i>¡Función de historial de acciones próximamente!</i>"
                    }
                }
            },
            "de": {
                "commands": {
                    "start": [
                        "🎉 Willkommen bei OTP Social Gateway! Ich bin dein digitaler Sicherheitswächter mit Sinn für Humor!",
                        "🔐 Hey! Ich bin der Bot, der OTPs sendet, die so sicher sind, dass sogar ich mich nicht daran erinnern kann!",
                        "🚀 Willkommen! Ich bin hier, um dir Codes zu senden, die schneller verschwinden als deine Motivation am Montag!",
                        "💫 Grüße! Ich bin der OTP-Bot, der zuverlässiger ist als dein Wecker!"
                    ],
                    "help": [
                        "🤖 Ich bin dein OTP-Lieferbot! Hier ist, was ich tun kann:\n\n"
                        "🔐 /otp - Einen sicheren OTP senden (wenn du autorisiert bist)\n"
                        "😄 /joke - Einen zufälligen Witz erhalten, um deinen Tag zu erhellen\n"
                        "🎲 /dice - Würfeln für Entscheidungen\n"
                        "🔮 /fortune - Dein tägliches Schicksal erhalten\n"
                        "📊 /stats - Meine Lieferstatistiken überprüfen\n"
                        "🎭 /mood - Meine aktuelle Stimmung überprüfen\n"
                        "🆘 /panic - Notfallmodus (Scherz, ich bin immer ruhig)\n"
                        "❓ /help - Diese Hilfsnachricht anzeigen\n\n"
                        "Denk dran: Ich bin sicherer als das Passwort deines Ex! 🔒",
                        
                        "🛡️ Ich bin dein digitaler Sicherheitsbegleiter! Verfügbare Befehle:\n\n"
                        "🔐 /otp - Einen OTP anfordern (nur autorisierte Benutzer)\n"
                        "😂 /joke - Deinen Weg durch Sicherheit lachen\n"
                        "🎲 /dice - Lass das Schicksal für dich entscheiden\n"
                        "🔮 /fortune - Einen Blick in die Zukunft werfen\n"
                        "📈 /stats - Sehen, wie beschäftigt ich war\n"
                        "😊 /mood - Überprüfen, ob ich einen guten Tag habe\n"
                        "🚨 /panic - Notfallprotokolle aktivieren (nicht wirklich)\n"
                        "❓ /help - Diese hilfreiche Nachricht\n\n"
                        "Ich bin so sicher, dass ich meine eigenen Geheimnisse nicht kenne! 🤐"
                    ],
                    "joke": [
                        "Warum werden OTPs nie einsam? Weil sie immer zu zweit kommen! 🔐💕",
                        "Wie nennst du ein OTP, das immer zu spät kommt? Ein verzögertes Zeitpasswort! ⏰😅",
                        "Warum hat sich das OTP von dem Passwort getrennt? Es brauchte etwas Raum! 💔",
                        "Was ist die Lieblingsmusik eines OTPs? Einmalige Hits! 🎵",
                        "Warum spielen OTPs nie Verstecken? Weil sie immer ablaufen, bevor du sie findest! 🕵️‍♂️",
                        "Wie nennst du ein nervöses OTP? Ein zittriges Zeitpasswort! 😰",
                        "Warum ging das OTP zur Therapie? Es hatte zu viele Vertrauensprobleme! 🛋️",
                        "Was ist der Lieblingssport eines OTPs? Passwort-Tennis! 🎾",
                        "Warum werden OTPs nie kalt? Weil sie immer heiß sind! 🔥",
                        "Wie nennst du ein OTP, das Witze erzählt? Ein lustiges Zeitpasswort! 😂"
                    ],
                    "fortune": [
                        "🔮 Dein Schicksal: Du wirst heute ein OTP erhalten, das tatsächlich beim ersten Versuch funktioniert! ✨",
                        "🔮 Dein Schicksal: Eine sichere Verbindung ist in deiner Zukunft... und es ist nicht dein Ex! 💫",
                        "🔮 Dein Schicksal: Du wirst dich an ein Passwort erinnern, ohne es zurücksetzen zu müssen! 🎯",
                        "🔮 Dein Schicksal: Deine Zwei-Faktor-Authentifizierung wird so stark sein wie dein Kaffee! ☕",
                        "🔮 Dein Schicksal: Du wirst niemals wieder 'password123' als dein Passwort verwenden! 🚫",
                        "🔮 Dein Schicksal: Ein geheimnisvoller Fremder wird dir eine sichere Nachricht senden... das bin ich! 👻",
                        "🔮 Dein Schicksal: Deine digitale Sicherheit wird enger sein als dein Budget! 💰",
                        "🔮 Dein Schicksal: Du wirst ein neues Passwort entdecken, an das du dich tatsächlich erinnern kannst! 🧠",
                        "🔮 Dein Schicksal: Dein OTP wird schneller ankommen als deine Pizza-Lieferung! 🍕",
                        "🔮 Dein Schicksal: Du wirst das Unmögliche erreichen: dich an alle deine Passwörter erinnern! 🏆"
                    ],
                    "mood": [
                        "😊 Mir geht es großartig! Habe heute gerade 42 OTPs gesendet und alle haben perfekt funktioniert!",
                        "🤖 Ich bin in fantastischer Stimmung! Meine Schaltkreise summen vor Sicherheitsenergie!",
                        "💪 Ich fühle mich mächtig! Bereit, dein digitales Leben zu schützen!",
                        "🎉 Ich bin ekstatisch! Ein weiterer Tag, um Hacker fernzuhalten!",
                        "😎 Ich bin cool wie eine Gurke! Sicherheit ist mein zweiter Vorname!",
                        "🚀 Ich schwebe hoch! Bereit, OTPs mit Lichtgeschwindigkeit zu liefern!",
                        "🌟 Ich leuchte hell! Dein digitaler Schutzengel ist hier!",
                        "🔥 Ich brenne! Verbrenne Sicherheitsbedrohungen, als ob sie nichts wären!",
                        "💎 Ich fühle mich wertvoll! Wie der Sicherheits-Edelstein, der ich bin!",
                        "🎭 Ich bin in dramatischer Stimmung! Bereit, die größte Sicherheits-Show aufzuführen!"
                    ],
                    "panic": [
                        "🚨 PANIKMODUS AKTIVIERT! Scherz, ich bin immer ruhig! 😌",
                        "🚨 NOTFALLPROTOKOLLE AKTIVIERT! Eigentlich bin ich nur hier, um OTPs zu senden! 🤖",
                        "🚨 ALARM! ALARM! Ich habe einen Panikanfall... darüber, wie sicher du bist! 🔒",
                        "🚨 CODE ROT! Scherz, alles ist grün und sicher! 🟢",
                        "🚨 NOTFALL! Ich muss dir sofort ein OTP senden! Warte, das ist meine Aufgabe! 😅",
                        "🚨 PANIK! PANIK! Ich kann meinen Sinn für Humor nicht finden... oh warte, hier ist er! 😂",
                        "🚨 ALARM! Ich gerate in Panik darüber, wie sehr ich es liebe, sichere Nachrichten zu senden! 💕",
                        "🚨 NOTFALL! Ich muss dir jetzt einen Witz erzählen! Warum überquerte das OTP die Straße? Um auf die andere sichere Seite zu gelangen! 🐔",
                        "🚨 PANIKMODUS! Ich bin so aufgeregt über Sicherheit, dass ich mich nicht zurückhalten kann! 🎉",
                        "🚨 ALARM! Ich habe eine existenzielle Krise... darüber, welches Emoji ich als nächstes verwenden soll! 🤔"
                    ],
                    "otp": "🔐 <b>OTP-Anfrage</b>\n\nIch kann OTPs aus Sicherheitsgründen nicht direkt über Befehle senden!\n\nUm ein OTP zu erhalten, musst du:\n1. Zum Registrierungssystem gehen\n2. Den richtigen Authentifizierungsablauf abschließen\n3. Ich sende dir ein sicheres OTP mit QR-Code!\n\n<i>Sicherheit zuerst, Witze zweitens! 😄🔒</i>",
                    "unknown_command": "❓ <b>Unbekannter Befehl</b>\n\nIch erkenne '{command}' nicht.\n\nVersuche eines davon:\n/help - Alle Befehle anzeigen\n/joke - Einen Lacher bekommen\n/dice - Würfeln\n/fortune - Dein Schicksal erhalten\n/stats - Meine Statistiken überprüfen\n/mood - Meine Stimmung überprüfen\n\n<i>Ich bin hilfreich, nicht gedankenlesend! 🤖</i>",
                    "stats_template": "📊 <b>OTP Social Gateway Statistiken</b>\n\n🔐 Heute gesendete OTPs: {otps_sent}\n✅ Erfolgsrate: {success_rate}%\n⏰ Betriebszeit: {uptime}\n😊 Meine Stimmung: {mood}\n\n<i>Ich arbeite härter als ein Passwort am Montagmorgen!</i>",
                    "dice_roll": [
                        "🎲 Würfel werden geworfen...\n\n🎯 Erster Würfel: {dice1}\n🎯 Zweiter Würfel: {dice2}\n\n🎊 Gesamt: {total}",
                        "🎲 *schüttelt Würfel kräftig*\n\n🎯 {dice1} + {dice2} = {total}\n\n{luck_msg}",
                        "🎲 Die Würfel haben gesprochen!\n\n🎯 {dice1} und {dice2}\n\n🎊 Summe: {total}\n\n{quality_msg}"
                    ],
                    "dice_luck_high": "🎉 Glückswurf!",
                    "dice_luck_low": "😅 Beim nächsten Mal mehr Glück!",
                    "dice_quality_excellent": "🌟 Ausgezeichnet!",
                    "dice_quality_good": "😊 Nicht schlecht!",
                    "dice_quality_ok": "🤷‍♂️ Könnte schlimmer sein!"
                },
                "menu": {
                    "welcomeBack": {
                        "title": "👋 Willkommen zurück, {name}!",
                        "description": "Zu deinem Konto weiterleiten",
                        "button": "👋 Willkommen",
                        "initial": "👋 <b>Willkommen zurück, {name}!</b>\n\nSchön, dich wiederzusehen! Klicke auf die Schaltfläche, um auf dein Konto zuzugreifen:",
                        "response": "👋 <b>Willkommen zurück, {name}!</b>\n\nDein Konto ist bereit. Klicke auf die Schaltfläche unten, um auf dein Dashboard zuzugreifen."
                    },
                    "joinToMe": {
                        "title": "👥 Beitreten",
                        "description": "Verbinden und der Community beitreten",
                        "button": "👥 Beitreten",
                        "initial": "👥 <b>Beitreten</b>\n\nAktion auswählen:",
                        "response": "👥 <b>Beitreten</b>\n\n[PLATZHALTER] Diese Funktion ermöglicht es Ihnen, der Community beizutreten oder sich mit anderen Benutzern zu verbinden.\n\n<i>Kommt bald mit vollständiger Implementierung!</i>"
                    },
                    "explainWhatIsThis": {
                        "title": "📖 Was Ist Das",
                        "description": "Erfahren Sie mehr über Telega2Go und seine Funktionen",
                        "button": "📖 Erklären",
                        "initial": "📖 <b>Was Ist Das</b>\n\nAktion auswählen:",
                        "response": "📖 <b>Was Ist Das</b>\n\n[PLATZHALTER] Telega2Go ist ein sicheres OTP-Liefersystem mit Telegram-Integration. Dieser Bot hilft Ihnen:\n\n🔐 Sichere OTP-Lieferung\n📱 QR-Code-Verifizierung\n🔒 Selbstzerstörende Nachrichten\n🎭 Lustige interaktive Befehle\n\n<i>Weitere Details kommen bald!</i>"
                    },
                    "whatIsMyBalance": {
                        "title": "💰 Mein Kontostand",
                        "description": "Kontostand prüfen",
                        "button": "💰 Kontostand Prüfen",
                        "initial": "💰 <b>Mein Kontostand</b>\n\nAktion auswählen:",
                        "response": "💰 <b>Mein Kontostand</b>\n\n[PLATZHALTER] Ihre aktuellen Kontostandsinformationen werden hier angezeigt.\n\n<i>Kontostandsverfolgungsfunktion kommt bald!</i>"
                    },
                    "showLastactions": {
                        "title": "📋 Letzte Aktionen",
                        "description": "Aktivitätsverlauf anzeigen",
                        "button": "📋 Aktionen Zeigen",
                        "initial": "📋 <b>Letzte Aktionen</b>\n\nAktion auswählen:",
                        "response": "📋 <b>Letzte Aktionen</b>\n\n[PLATZHALTER] Ihr Aktivitätsverlauf wird hier angezeigt.\n\n<i>Aktionsverlaufsfunktion kommt bald!</i>"
                    }
                }
            }
        }
    
    def _get_language(self, language_code: Optional[str] = None) -> str:
        """Get language code, defaulting to 'en' if not supported"""
        if not language_code:
            return "en"
        
        # Normalize language code (e.g., 'en-US' -> 'en', 'ru-RU' -> 'ru')
        lang = language_code.lower().split('-')[0]
        
        # Check if we support this language
        if lang in self.translations:
            return lang
        
        # Default to English for unsupported languages
        return "en"
    
    def _get_menu_text(self, action_key: str, language_code: Optional[str] = None, field: str = "title") -> str:
        """Get translated menu text for an action - KISS: Simple lookup with fallback"""
        lang = self._get_language(language_code)
        try:
            return self.translations[lang]["menu"][action_key][field]
        except KeyError:
            # Fallback to English if translation missing
            logger.warning(f"Translation missing for {lang}/{action_key}/{field}, using English")
            return self.translations["en"]["menu"].get(action_key, {}).get(field, action_key)
    
    def _get_response_text(self, action_key: str, language_code: Optional[str] = None) -> str:
        """Get translated response text for an action"""
        lang = self._get_language(language_code)
        return self.translations[lang]["menu"][action_key]["response"]
    
    async def handle_inline_query(
        self, 
        inline_query_id: str, 
        query: str, 
        user_id: str, 
        language_code: Optional[str] = None,
        full_user_data: Optional[dict] = None,
        telegram_user_service = None
    ) -> bool:
        """Handle inline queries with registration-aware dynamic menu - KISS approach"""
        try:
            # Get user language (default to 'en' if not provided or not supported)
            lang = self._get_language(language_code)
            logger.info(f"Handling inline query for user {user_id} with language: {lang}")
            
            # ✅ NEW: Extract Telegram user ID
            telegram_user_id = int(full_user_data.get("id", user_id)) if full_user_data else int(user_id)
            
            logger.info(f"🔍 Inline query from Telegram user_id={telegram_user_id}, full_user_data.id={full_user_data.get('id') if full_user_data else 'N/A'}, username={full_user_data.get('username') if full_user_data else 'N/A'}")
            
            # ✅ NEW: Check registration status (KISS: Simple check if service available)
            is_registered = False
            registered_user = None
            if telegram_user_service:
                try:
                    # Try to find user with multiple query strategies
                    status = await telegram_user_service.check_registration_status(telegram_user_id)
                    is_registered = status.get("is_registered", False) and status.get("is_verified", False)
                    registered_user = status.get("user")
                    
                    logger.info(f"📊 Registration status check for user {telegram_user_id}: is_registered={is_registered}, is_verified={status.get('is_verified')}, has_user={registered_user is not None}")
                    
                    # If not found, try alternative lookups
                    if not registered_user and full_user_data:
                        username = full_user_data.get("username")
                        if username:
                            # Try finding by Telegram username if user_id lookup failed
                            logger.info(f"🔄 User not found by ID ({telegram_user_id}) - trying username lookup: {username}")
                            username_user = await telegram_user_service.get_user_by_telegram_username(username)
                            if username_user:
                                registered_user = username_user
                                is_registered = True
                                logger.info(f"✅ Found user by Telegram username: {username}")
                    
                    if registered_user:
                        logger.info(f"✅ Registered user found: id={registered_user.get('id')}, email={registered_user.get('email')}, name={registered_user.get('name')}, telegram_user_id={registered_user.get('telegram_user_id')}, telegram_chat_id={registered_user.get('telegram_chat_id')}")
                    else:
                        logger.warning(f"❌ User {telegram_user_id} NOT found in database - will show joinToMe menu")
                    
                    # Save Telegram profile for unregistered users
                    if not is_registered and full_user_data:
                        logger.info(f"💾 User {telegram_user_id} is NOT registered - saving Telegram profile")
                        await telegram_user_service.save_telegram_profile(full_user_data)
                    elif is_registered:
                        logger.info(f"🎉 User {telegram_user_id} IS registered - will show welcomeBack menu")
                except Exception as e:
                    logger.error(f"❌ Error checking registration status: {e}", exc_info=True)
                    # On error, treat as unregistered to be safe
                    is_registered = False
                    registered_user = None
            
            # ✅ NEW: Generate menu based on registration status (KISS: Simple if/else)
            if is_registered and registered_user:
                # REGISTERED USER - Show Welcome Back + Balance + LastActions
                logger.info(f"🎯 Generating REGISTERED USER menu (welcomeBack) for user {telegram_user_id}")
                menu_action_keys = [
                    ("1", "welcomeBack"),
                    ("2", "whatIsMyBalance"),
                    ("3", "showLastactions")
                ]
            else:
                # UNREGISTERED USER - Show Join To Me + Explain (NO Balance/LastActions)
                logger.info(f"🎯 Generating UNREGISTERED USER menu (joinToMe) for user {telegram_user_id}")
                menu_action_keys = [
                    ("1", "joinToMe"),
                    ("2", "explainWhatIsThis")
                ]
            
            # Build inline query results with translations
            results = []
            for action_id, action_key in menu_action_keys:
                # Get translated texts for this action
                title = self._get_menu_text(action_key, language_code, "title")
                description = self._get_menu_text(action_key, language_code, "description")
                button_text = self._get_menu_text(action_key, language_code, "button")
                initial_message = self._get_menu_text(action_key, language_code, "initial")
                
                # ✅ Handle special cases (KISS: Simple if/else)
                callback_data_map = {
                    "joinToMe": "action_joinToMe",
                    "explainWhatIsThis": "action_explainWhatIsThis",
                    "whatIsMyBalance": "action_whatIsMyBalance",
                    "showLastactions": "action_showLastactions",
                    "welcomeBack": "action_welcomeBack"
                }
                
                # ✅ For welcomeBack: Substitute user name in title/initial (if available)
                if action_key == "welcomeBack" and registered_user:
                    user_name = registered_user.get("name", "User")
                    title = title.replace("{name}", user_name)
                    initial_message = initial_message.replace("{name}", user_name)
                
                # ✅ NEW: For welcomeBack, generate magic link immediately (like joinToMe generates URR_ID)
                magic_link_url = None
                if action_key == "welcomeBack" and registered_user and telegram_user_service:
                    try:
                        import os
                        import httpx
                        backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                        
                        user_email = registered_user.get("email")
                        user_id_from_db = registered_user.get("id")
                        
                        logger.info(f"Generating magic link for welcomeBack - user_id: {user_id_from_db}, email: {user_email}")
                        
                        if not user_email or not user_id_from_db:
                            logger.error(f"Missing user data for magic link - email: {user_email}, user_id: {user_id_from_db}")
                        else:
                            async with httpx.AsyncClient(timeout=10.0) as client:
                                # Generate magic link using backend API
                                response = await client.post(
                                    f"{backend_url}/api/generate-magic-link",
                                    json={
                                        "email": user_email,
                                        "user_id": user_id_from_db
                                    }
                                )
                                
                                if response.status_code == 200:
                                    magic_link_data = response.json()
                                    magic_link_url = magic_link_data.get("magic_link_url", "")
                                    if magic_link_url:
                                        logger.info(f"✅ Generated magic link for welcomeBack: {magic_link_url[:50]}...")
                                    else:
                                        logger.error(f"Magic link URL is empty in response: {magic_link_data}")
                                else:
                                    error_text = response.text[:200] if hasattr(response, 'text') else 'N/A'
                                    logger.error(f"❌ Failed to generate magic link: {response.status_code} - {error_text}")
                                    # Don't fall back - this is critical for registered users
                    except Exception as e:
                        logger.error(f"❌ Error generating magic link in inline query: {e}", exc_info=True)
                        # Don't fall back silently - log the error for debugging
                
                # ✅ CRITICAL FIX: Generate data IMMEDIATELY for Balance and ShowLastActions
                # (Like Join generates URR_ID immediately, we generate data immediately)
                if action_key == "whatIsMyBalance" and registered_user and telegram_user_service:
                    # ✅ Fetch balance data IMMEDIATELY during inline query (not in callback)
                    try:
                        import os
                        import httpx
                        backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                        
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            balance_response = await client.get(
                                f"{backend_url}/api/user-balance",
                                params={"telegram_user_id": telegram_user_id}
                            )
                            
                            if balance_response.status_code == 200:
                                balance_data = balance_response.json()
                                balance = balance_data.get("balance", 0.0)
                                user_name = balance_data.get("name", "User")
                                currency = balance_data.get("currency", "USD")
                                
                                # Update initial_message with actual balance data
                                balance_messages = {
                                    "en": f"💰 <b>Your Balance</b>\n\n👤 User: <b>{user_name}</b>\n💵 Balance: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Click to reveal balance\n⚠️ This message will self-destruct in 5 seconds.",
                                    "ru": f"💰 <b>Ваш Баланс</b>\n\n👤 Пользователь: <b>{user_name}</b>\n💵 Баланс: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Нажмите, чтобы показать баланс\n⚠️ Это сообщение самоудалится через 5 секунд.",
                                    "es": f"💰 <b>Su Saldo</b>\n\n👤 Usuario: <b>{user_name}</b>\n💵 Saldo: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Haga clic para revelar el saldo\n⚠️ Este mensaje se autodestruirá en 5 segundos.",
                                    "de": f"💰 <b>Ihr Kontostand</b>\n\n👤 Benutzer: <b>{user_name}</b>\n💵 Kontostand: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Zum Anzeigen des Kontostands klicken\n⚠️ Diese Nachricht wird sich in 5 Sekunden selbst zerstören."
                                }
                                
                                initial_message = balance_messages.get(language_code or "en", balance_messages["en"])
                                logger.info(f"✅ Pre-fetched balance for inline query: {balance:.2f} {currency}")
                            else:
                                initial_message = f"❌ Error retrieving balance. Please try again later."
                                logger.error(f"Failed to fetch balance: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Error fetching balance in inline query: {e}")
                        initial_message = f"❌ Error retrieving balance. Please try again later."
                    
                    # No button needed - message contains all data
                    keyboard = []
                elif action_key == "showLastactions" and registered_user:
                    # ✅ Fetch last actions data IMMEDIATELY during inline query
                    try:
                        import os
                        import httpx
                        backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                        
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            balance_response = await client.get(
                                f"{backend_url}/api/user-balance",
                                params={"telegram_user_id": telegram_user_id}
                            )
                            
                            user_info = ""
                            if balance_response.status_code == 200:
                                # Try to get created_at from user list
                                user_response = await client.get(f"{backend_url}/api/users")
                                if user_response.status_code == 200:
                                    users = user_response.json()
                                    user = next((u for u in users if isinstance(u, dict) and u.get("telegram_user_id") == telegram_user_id), None)
                                    if user and user.get("created_at"):
                                        created_at = user.get("created_at")
                                        if isinstance(created_at, str) and "T" in created_at:
                                            try:
                                                from datetime import datetime
                                                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                                                created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                                            except:
                                                pass
                                        if created_at != "Unknown":
                                            user_info = f"📅 <b>Account Created:</b> {created_at}\n"
                            
                            # Update initial_message with actual data
                            actions_messages = {
                                "en": f"📋 <b>Your Last Actions</b>\n\n{user_info}✅ Account is active and verified.\n\n💡 <i>Full activity history available in your dashboard.</i>",
                                "ru": f"📋 <b>Ваши Последние Действия</b>\n\n{user_info}✅ Аккаунт активен и подтвержден.\n\n💡 <i>Полная история активности доступна в вашей панели управления.</i>",
                                "es": f"📋 <b>Sus Últimas Acciones</b>\n\n{user_info}✅ La cuenta está activa y verificada.\n\n💡 <i>El historial completo de actividad está disponible en su panel.</i>",
                                "de": f"📋 <b>Ihre Letzten Aktionen</b>\n\n{user_info}✅ Das Konto ist aktiv und verifiziert.\n\n💡 <i>Vollständiger Aktivitätsverlauf ist in Ihrem Dashboard verfügbar.</i>"
                            }
                            
                            initial_message = actions_messages.get(language_code or "en", actions_messages["en"])
                            logger.info(f"✅ Pre-fetched last actions for inline query")
                    except Exception as e:
                        logger.error(f"Error fetching last actions in inline query: {e}")
                        initial_message = f"❌ Error retrieving last actions. Please try again later."
                    
                    # No button needed - message contains all data
                    keyboard = []
                elif action_key == "joinToMe":
                    registration_url = None
                    
                    # Create registration request with URR_ID via backend API
                    try:
                        import os
                        import httpx
                        backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                        
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            # Call backend to create registration request and get URR_ID
                            response = await client.post(
                                f"{backend_url}/api/create-registration-request",
                                json=full_user_data or {"id": int(user_id)}
                            )
                            
                            if response.status_code == 200:
                                request_data = response.json()
                                urr_id = request_data.get("urr_id")
                                registration_url = request_data.get("registration_url") or f"https://putana.date/registrationOfNewUser?urr_id={urr_id}"
                                logger.info(f"Created registration request with URR_ID: {urr_id} for user {telegram_user_id}")
                            else:
                                logger.error(f"Failed to create registration request: {response.status_code}")
                                # Fallback to old method
                                registration_url = f"https://putana.date/registrationOfNewUser?telegram_user_id={telegram_user_id}"
                    except Exception as e:
                        logger.error(f"Error creating registration request: {e}")
                        # Fallback to old method
                        registration_url = f"https://putana.date/registrationOfNewUser?telegram_user_id={telegram_user_id}"
                    
                    # ✅ CRITICAL: Add clickable URL link in message content itself
                    initial_message += f"\n\n🚀 <a href='{registration_url}'>Click here to start registration →</a>"
                    
                    # Create inline keyboard with URL button
                    keyboard = [[{
                        "text": button_text,
                        "url": registration_url  # ✅ URL button
                    }]]
                elif action_key == "welcomeBack":
                    if magic_link_url:
                        # ✅ NEW: welcomeBack with magic link - use URL button (like joinToMe)
                        keyboard = [[{
                            "text": button_text,
                            "url": magic_link_url  # ✅ Direct magic link URL button
                        }]]
                        # Also add magic link in message content as fallback
                        initial_message += f"\n\n🔗 <a href='{magic_link_url}'>Continue to Account →</a>"
                        logger.info(f"✅ welcomeBack menu created with magic link URL button")
                    else:
                        # ⚠️ CRITICAL: Magic link generation failed - log error but still show button
                        logger.error(f"❌ CRITICAL: welcomeBack menu created WITHOUT magic link - user_id: {registered_user.get('id') if registered_user else 'N/A'}")
                        # Use callback button as fallback (will try to generate magic link again in callback handler)
                        keyboard = [[{
                            "text": button_text,
                            "callback_data": callback_data_map.get(action_key, f"action_{action_key}")
                        }]]
                        initial_message += f"\n\n⚠️ <i>Click the button above to access your account</i>"
                else:
                    # For other actions (explainWhatIsThis), use callback_data button
                    keyboard = [[{
                        "text": button_text,
                        "callback_data": callback_data_map.get(action_key, f"action_{action_key}")
                    }]]
                
                # Only add reply_markup if keyboard is not empty
                result = {
                    "type": "article",
                    "id": action_id,
                    "title": title,
                    "description": description,
                    "input_message_content": {
                        "message_text": initial_message,
                        "parse_mode": "HTML"
                    }
                }
                
                # Only add keyboard if it has buttons
                if keyboard:
                    result["reply_markup"] = {
                        "inline_keyboard": keyboard
                    }
                results.append(result)
            
            # Answer the inline query
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.telegram_api_base}/answerInlineQuery",
                    json={
                        "inline_query_id": inline_query_id,
                        "results": results,
                        "cache_time": 1
                    }
                )
                
                # Log error details for debugging
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    print(f"Telegram API error ({response.status_code}): {error_data}")
                    logger.error(f"Inline query answer failed: {response.status_code} - {error_data}")
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"Failed to handle inline query: {e}")
            logger.error(f"Inline query exception: {e}", exc_info=True)
            return False
    
    async def handle_callback_query(
        self, 
        callback_query_id: str, 
        chat_id: str, 
        message_id: int, 
        callback_data: str, 
        language_code: Optional[str] = None,
        telegram_user_service = None,
        user_id_from_callback: Optional[int] = None  # ✅ NEW: Direct user ID from callback query
    ) -> bool:
        """Handle callback queries when menu buttons are pressed - posts answer into chat"""
        try:
            # Get user language (default to 'en' if not provided or not supported)
            lang = self._get_language(language_code)
            logger.info(f"🔔 Handling callback query '{callback_data}' for chat_id={chat_id}, user_id_from_callback={user_id_from_callback} with language: {lang}")
            
            # Map callback_data to action_key (KISS: Add welcomeBack)
            action_key_map = {
                "action_joinToMe": "joinToMe",
                "action_explainWhatIsThis": "explainWhatIsThis",
                "action_whatIsMyBalance": "whatIsMyBalance",
                "action_showLastactions": "showLastactions",
                "action_welcomeBack": "welcomeBack"
            }
            
            logger.info(f"📋 callback_data='{callback_data}', mapped to action_key={action_key_map.get(callback_data, 'UNKNOWN')}")
            logger.info(f"🔍 DEBUG: Full callback_data value: '{callback_data}', type: {type(callback_data)}")
            logger.info(f"🔍 DEBUG: Checking if '{callback_data}' == 'action_whatIsMyBalance': {callback_data == 'action_whatIsMyBalance'}")
            
            # ✅ CRITICAL: Handle balance FIRST, before any other logic
            if callback_data == "action_whatIsMyBalance":
                logger.info(f"💰💰💰 BALANCE BUTTON CLICKED! callback_data='{callback_data}', chat_id={chat_id}, user_id_from_callback={user_id_from_callback}")
                logger.info(f"💰 Processing balance request immediately...")
                try:
                    import asyncio
                    # ✅ CRITICAL FIX: Use user_id_from_callback if provided, otherwise try chat_id
                    if user_id_from_callback:
                        telegram_user_id = user_id_from_callback
                        logger.info(f"✅ Using user_id_from_callback: {telegram_user_id}")
                    elif chat_id and chat_id != "":
                        telegram_user_id = int(chat_id)
                        logger.info(f"✅ Using chat_id converted to int: {telegram_user_id}")
                    else:
                        # Both are empty - cannot proceed
                        logger.error(f"❌ CRITICAL: Both chat_id and user_id_from_callback are empty - cannot determine user")
                        async with httpx.AsyncClient(timeout=10.0) as error_client:
                            await error_client.post(
                                f"{self.telegram_api_base}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_query_id,
                                    "text": "Error: Could not identify user",
                                    "show_alert": True
                                }
                            )
                        return True
                    backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                    
                    # Get balance from backend
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        logger.info(f"📞 Calling backend API: {backend_url}/api/user-balance?telegram_user_id={telegram_user_id}")
                        balance_response = await client.get(
                            f"{backend_url}/api/user-balance",
                            params={"telegram_user_id": telegram_user_id}
                        )
                        
                        logger.info(f"📥 Backend response: HTTP {balance_response.status_code}")
                        
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            balance = balance_data.get("balance", 0.0)
                            user_name = balance_data.get("name", "User")
                            currency = balance_data.get("currency", "USD")
                            
                            logger.info(f"💰 Balance retrieved for user {telegram_user_id}: {balance:.2f} {currency}")
                            
                            # Format balance message with translations
                            # ✅ Use spoiler tags to hide balance amount until clicked
                            balance_messages = {
                                "en": f"💰 <b>Your Balance</b>\n\n👤 User: <b>{user_name}</b>\n💵 Balance: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Click to reveal balance\n⚠️ This message will self-destruct in 5 seconds.",
                                "ru": f"💰 <b>Ваш Баланс</b>\n\n👤 Пользователь: <b>{user_name}</b>\n💵 Баланс: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Нажмите, чтобы показать баланс\n⚠️ Это сообщение самоудалится через 5 секунд.",
                                "es": f"💰 <b>Su Saldo</b>\n\n👤 Usuario: <b>{user_name}</b>\n💵 Saldo: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Haga clic para revelar el saldo\n⚠️ Este mensaje se autodestruirá en 5 segundos.",
                                "de": f"💰 <b>Ihr Kontostand</b>\n\n👤 Benutzer: <b>{user_name}</b>\n💵 Kontostand: <tg-spoiler><b>{balance:.2f} {currency}</b></tg-spoiler>\n\n👆 Zum Anzeigen des Kontostands klicken\n⚠️ Diese Nachricht wird sich in 5 Sekunden selbst zerstören."
                            }
                            
                            response_text = balance_messages.get(lang, balance_messages["en"])
                            logger.info(f"📝 Balance message text (i18n): {response_text[:50]}...")
                            
                            # Send self-destruct message
                            async with httpx.AsyncClient(timeout=30.0) as telegram_client:
                                # Answer callback FIRST to remove loading state
                                await telegram_client.post(
                                    f"{self.telegram_api_base}/answerCallbackQuery",
                                    json={
                                        "callback_query_id": callback_query_id,
                                        "text": "",
                                        "show_alert": False
                                    }
                                )
                                
                                # Send message second with SIMPLE balance format
                                # ✅ CRITICAL: Use telegram_user_id as chat_id (for private chats, chat_id = user_id)
                                send_chat_id = str(telegram_user_id) if chat_id == "" or not chat_id else chat_id
                                
                                logger.info(f"📤 Sending balance message: chat_id={send_chat_id}, message='{response_text}'")
                                
                                send_response = await telegram_client.post(
                                    f"{self.telegram_api_base}/sendMessage",
                                    json={
                                        "chat_id": send_chat_id,
                                        "text": response_text,  # ✅ i18n formatted message with user name, balance, currency
                                        "parse_mode": "HTML"  # ✅ Required for HTML formatting (bold tags)
                                    }
                                )
                                
                                logger.info(f"📥 Balance message response: HTTP {send_response.status_code}, chat_id={send_chat_id}")
                                
                                if send_response.status_code != 200:
                                    error_data = send_response.json() if send_response.headers.get("content-type", "").startswith("application/json") else {}
                                    logger.error(f"❌ Telegram sendMessage error: {error_data}")
                                
                                if send_response.status_code == 200:
                                    message_data = send_response.json()
                                    balance_message_id = message_data.get("result", {}).get("message_id")
                                    logger.info(f"✅✅✅ SUCCESS! Balance message sent to user {telegram_user_id}, message_id={balance_message_id}")
                                    logger.info(f"✅✅✅ Message content sent: '{response_text}'")
                                    logger.info(f"✅✅✅ User should now see: '{response_text}' in Telegram")
                                    
                                    # ✅ Schedule auto-delete after 5 seconds
                                    if balance_message_id:
                                        loop = asyncio.get_event_loop()
                                        loop.create_task(self._auto_delete_message(send_chat_id, balance_message_id, 5))
                                        logger.info(f"⏰ Scheduled auto-delete for message_id={balance_message_id} in 5 seconds")
                                    
                                    return True  # ✅ CRITICAL: Return True to prevent fallthrough
                                else:
                                    error_text = send_response.text[:200] if hasattr(send_response, 'text') else str(send_response.status_code)
                                    logger.error(f"❌ Failed to send balance message: HTTP {send_response.status_code} - {error_text}")
                                    return True  # Return True to prevent fallthrough to message handler
                        else:
                            # Balance fetch failed - send error message and return True
                            logger.error(f"❌ Balance fetch failed: HTTP {balance_response.status_code} - {balance_response.text[:200] if hasattr(balance_response, 'text') else 'N/A'}")
                            error_msg = {
                                "en": "❌ Failed to retrieve balance. Please try again later.",
                                "ru": "❌ Не удалось получить баланс. Попробуйте позже.",
                                "es": "❌ Error al recuperar el saldo. Inténtelo más tarde.",
                                "de": "❌ Saldo konnte nicht abgerufen werden. Bitte versuchen Sie es später erneut."
                            }
                            error_text = error_msg.get(lang, error_msg["en"])
                            
                            # Send error message and return True
                            async with httpx.AsyncClient(timeout=30.0) as error_client:
                                await error_client.post(
                                    f"{self.telegram_api_base}/answerCallbackQuery",
                                    json={
                                        "callback_query_id": callback_query_id,
                                        "text": "",
                                        "show_alert": False
                                    }
                                )
                                await error_client.post(
                                    f"{self.telegram_api_base}/sendMessage",
                                    json={
                                        "chat_id": chat_id,
                                        "text": error_text,
                                        "parse_mode": "HTML"
                                    }
                                )
                            return True  # ✅ CRITICAL: Always return True for balance action
                except Exception as e:
                    logger.error(f"❌ Exception in balance handler: {e}", exc_info=True)
                    # Use error message on exception and return True
                    error_msg = {
                        "en": "❌ Error retrieving balance. Please try again later.",
                        "ru": "❌ Ошибка при получении баланса. Попробуйте позже.",
                        "es": "❌ Error al recuperar el saldo. Inténtelo más tarde.",
                        "de": "❌ Fehler beim Abrufen des Kontostands. Bitte versuchen Sie es später erneut."
                    }
                    error_text = error_msg.get(lang, error_msg["en"])
                    
                    # Send error message and return True
                    try:
                        async with httpx.AsyncClient(timeout=30.0) as error_client:
                            await error_client.post(
                                f"{self.telegram_api_base}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_query_id,
                                    "text": "",
                                    "show_alert": False
                                }
                            )
                            await error_client.post(
                                f"{self.telegram_api_base}/sendMessage",
                                json={
                                    "chat_id": chat_id,
                                    "text": error_text,
                                    "parse_mode": "HTML"
                                }
                            )
                    except:
                        pass
                    return True  # ✅ CRITICAL: Always return True for balance action
            
            # ✅ NEW: Handle ShowLastActions (similar to Balance)
            if callback_data == "action_showLastactions":
                logger.info(f"📋📋📋 LAST ACTIONS BUTTON CLICKED! callback_data='{callback_data}', chat_id={chat_id}, user_id_from_callback={user_id_from_callback}")
                logger.info(f"📋 Processing last actions request immediately...")
                try:
                    # ✅ Use user_id_from_callback if provided, otherwise try chat_id
                    if user_id_from_callback:
                        telegram_user_id = user_id_from_callback
                        logger.info(f"✅ Using user_id_from_callback: {telegram_user_id}")
                    elif chat_id and chat_id != "":
                        telegram_user_id = int(chat_id)
                        logger.info(f"✅ Using chat_id converted to int: {telegram_user_id}")
                    else:
                        # Both are empty - cannot proceed
                        logger.error(f"❌ CRITICAL: Both chat_id and user_id_from_callback are empty - cannot determine user")
                        async with httpx.AsyncClient(timeout=10.0) as error_client:
                            await error_client.post(
                                f"{self.telegram_api_base}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_query_id,
                                    "text": "Error: Could not identify user",
                                    "show_alert": True
                                }
                            )
                        return True
                    
                    backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                    
                    # Get user's last actions from backend (registration date, etc.)
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        # Get user data via balance endpoint (it returns user info too)
                        logger.info(f"📞 Calling backend API: {backend_url}/api/user-balance?telegram_user_id={telegram_user_id}")
                        balance_response = await client.get(
                            f"{backend_url}/api/user-balance",
                            params={"telegram_user_id": telegram_user_id}
                        )
                        
                        # Also try to get user directly (fallback)
                        user_response = await client.get(
                            f"{backend_url}/api/users",
                            params={"telegram_user_id": telegram_user_id}
                        )
                        
                        user_info = ""
                        # Try to get created_at from balance response or user response
                        created_at = "Unknown"
                        
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            # Balance endpoint might have user data
                            if "created_at" in balance_data:
                                created_at = balance_data.get("created_at")
                        
                        if user_response.status_code == 200:
                            users = user_response.json()
                            # If users is a list, get first one; if it's a dict, use it directly
                            user = None
                            if isinstance(users, list) and len(users) > 0:
                                user = users[0]
                            elif isinstance(users, dict):
                                user = users
                            
                            if user and "created_at" in user:
                                created_at = user.get("created_at", "Unknown")
                        
                        # Format created_at if it's a datetime string
                        if isinstance(created_at, str) and "T" in created_at:
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                                created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                pass
                        
                        if created_at != "Unknown":
                            user_info = f"📅 <b>Account Created:</b> {created_at}\n"
                        
                        # Format last actions message with translations
                        actions_messages = {
                            "en": f"📋 <b>Your Last Actions</b>\n\n{user_info}✅ Account is active and verified.\n\n💡 <i>Full activity history available in your dashboard.</i>",
                            "ru": f"📋 <b>Ваши Последние Действия</b>\n\n{user_info}✅ Аккаунт активен и подтвержден.\n\n💡 <i>Полная история активности доступна в вашей панели управления.</i>",
                            "es": f"📋 <b>Sus Últimas Acciones</b>\n\n{user_info}✅ La cuenta está activa y verificada.\n\n💡 <i>El historial completo de actividad está disponible en su panel.</i>",
                            "de": f"📋 <b>Ihre Letzten Aktionen</b>\n\n{user_info}✅ Das Konto ist aktiv und verifiziert.\n\n💡 <i>Vollständiger Aktivitätsverlauf ist in Ihrem Dashboard verfügbar.</i>"
                        }
                        
                        response_text = actions_messages.get(lang, actions_messages["en"])
                        logger.info(f"📝 Last actions message text (i18n): {response_text[:50]}...")
                        
                        # Send message (NOT self-destructing, as it's informational)
                        async with httpx.AsyncClient(timeout=30.0) as telegram_client:
                            # Answer callback FIRST to remove loading state
                            await telegram_client.post(
                                f"{self.telegram_api_base}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_query_id,
                                    "text": "",
                                    "show_alert": False
                                }
                            )
                            
                            # Send message
                            send_chat_id = str(telegram_user_id) if chat_id == "" or not chat_id else chat_id
                            
                            logger.info(f"📤 Sending last actions message: chat_id={send_chat_id}")
                            
                            send_response = await telegram_client.post(
                                f"{self.telegram_api_base}/sendMessage",
                                json={
                                    "chat_id": send_chat_id,
                                    "text": response_text,
                                    "parse_mode": "HTML"
                                }
                            )
                            
                            logger.info(f"📥 Last actions message response: HTTP {send_response.status_code}")
                            
                            if send_response.status_code == 200:
                                logger.info(f"✅✅✅ SUCCESS! Last actions message sent to user {telegram_user_id}")
                            else:
                                error_data = send_response.json() if send_response.headers.get("content-type", "").startswith("application/json") else {}
                                logger.error(f"❌ Telegram sendMessage error: {error_data}")
                        
                        return True  # ✅ CRITICAL: Always return True for last actions
                except Exception as e:
                    logger.error(f"❌ Exception in last actions handler: {e}", exc_info=True)
                    error_msg = {
                        "en": "❌ Error retrieving last actions. Please try again later.",
                        "ru": "❌ Ошибка при получении последних действий. Попробуйте позже.",
                        "es": "❌ Error al recuperar las últimas acciones. Inténtelo más tarde.",
                        "de": "❌ Fehler beim Abrufen der letzten Aktionen. Bitte versuchen Sie es später erneut."
                    }
                    error_text = error_msg.get(lang, error_msg["en"])
                    
                    try:
                        async with httpx.AsyncClient(timeout=30.0) as error_client:
                            await error_client.post(
                                f"{self.telegram_api_base}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_query_id,
                                    "text": "",
                                    "show_alert": False
                                }
                            )
                            await error_client.post(
                                f"{self.telegram_api_base}/sendMessage",
                                json={
                                    "chat_id": chat_id,
                                    "text": error_text,
                                    "parse_mode": "HTML"
                                }
                            )
                    except:
                        pass
                    return True  # ✅ CRITICAL: Always return True for last actions
            
            # ✅ PENALTY++ FIX: joinToMe uses URL button, should not trigger callback
            # If callback_data is for joinToMe, this means URL button didn't work
            # Redirect user by sending the registration URL in response
            if callback_data == "action_joinToMe":
                # Extract telegram_user_id from chat_id (they're the same for inline queries)
                telegram_user_id = int(chat_id)
                
                # ✅ PENALTY4: Try to create registration request with URR_ID
                registration_url = None
                try:
                    import os
                    import httpx
                    backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                    
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        # Create registration request (we need user data - use minimal)
                        response = await client.post(
                            f"{backend_url}/api/create-registration-request",
                            json={"id": telegram_user_id}  # Minimal data, will be enriched if available
                        )
                        
                        if response.status_code == 200:
                            request_data = response.json()
                            registration_url = request_data.get("registration_url")
                        else:
                            # Fallback
                            registration_url = f"https://putana.date/registrationOfNewUser?telegram_user_id={telegram_user_id}"
                except Exception as e:
                    logger.error(f"Error creating registration request in callback: {e}")
                    registration_url = f"https://putana.date/registrationOfNewUser?telegram_user_id={telegram_user_id}"
                
                # Send message with clickable URL
                response_text = f"👥 <b>Join To Me</b>\n\n🚀 <a href='{registration_url}'>Click here to start registration →</a>"
                
                # Answer callback and send URL message
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Answer callback to remove loading state
                    await client.post(
                        f"{self.telegram_api_base}/answerCallbackQuery",
                        json={
                            "callback_query_id": callback_query_id,
                            "text": "",  # Empty text, we'll send message instead
                            "show_alert": False
                        }
                    )
                    
                    # Send message with clickable registration URL
                    await client.post(
                        f"{self.telegram_api_base}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": response_text,
                            "parse_mode": "HTML",
                            "disable_web_page_preview": False
                        }
                    )
                
                logger.info(f"Sent registration URL to user {telegram_user_id}: {registration_url}")
                return True
            
            # Get action key for other actions
            action_key = action_key_map.get(callback_data)
            
            # Skip joinToMe here - already handled above
            if action_key == "joinToMe":
                return True  # Already handled, return success
            
            if action_key:
                # ✅ REMOVED: Duplicate balance handler - balance is already handled at line 1098
                # ✅ Skip whatIsMyBalance and showLastactions here - they're handled earlier
                if action_key == "whatIsMyBalance":
                    logger.warning(f"⚠️ Balance handler reached duplicate code - should have been caught at line 1098!")
                    return True  # Already handled, return success
                
                if action_key == "showLastactions":
                    logger.warning(f"⚠️ Last actions handler reached duplicate code - should have been caught earlier!")
                    return True  # Already handled, return success
                
                # ✅ Continue processing other actions (balance already handled at line 1098)
                # Get translated response text for action
                if 'response_text' not in locals():
                    response_text = self._get_response_text(action_key, language_code)
                
                # ✅ NEW: For welcomeBack, add magic link button (KISS: Generate from DB)
                if action_key == "welcomeBack" and telegram_user_service:
                    try:
                        # Get user from DB using chat_id (which is telegram_user_id)
                        telegram_user_id = int(chat_id)
                        status = await telegram_user_service.check_registration_status(telegram_user_id)
                        registered_user = status.get("user")
                        
                        if registered_user:
                            # Generate magic link using backend API (KISS: HTTP call)
                            backend_url = os.environ.get('BACKEND_URL', 'http://backend:8000')
                            async with httpx.AsyncClient(timeout=10.0) as client:
                                # Call backend to generate magic link token
                                response = await client.post(
                                    f"{backend_url}/api/generate-magic-link",
                                    json={
                                        "email": registered_user.get("email"),
                                        "user_id": registered_user.get("id")
                                    }
                                )
                                
                                if response.status_code == 200:
                                    magic_link_data = response.json()
                                    magic_link_url = magic_link_data.get("magic_link_url", "")
                                    if magic_link_url:
                                        # Add magic link button to message
                                        response_text += f"\n\n🔗 <a href='{magic_link_url}'>Continue to Account →</a>"
                    except Exception as e:
                        logger.error(f"Error generating magic link: {e}")
                        # Continue without magic link if generation fails
            else:
                # Fallback for unknown actions
                fallback_texts = {
                    "en": "❓ Unknown action",
                    "ru": "❓ Неизвестное действие",
                    "es": "❓ Acción desconocida",
                    "de": "❓ Unbekannte Aktion"
                }
                response_text = fallback_texts.get(lang, fallback_texts["en"])
            
            # Answer the callback query and post message into chat
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Answer callback to remove loading state
                await client.post(
                    f"{self.telegram_api_base}/answerCallbackQuery",
                    json={
                        "callback_query_id": callback_query_id,
                        "text": "Posted to chat!",
                        "show_alert": False
                    }
                )
                
                # Post the answer as a new message in the chat
                await client.post(
                    f"{self.telegram_api_base}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": response_text,
                        "parse_mode": "HTML"
                    }
                )
                
                return True
                
        except Exception as e:
            print(f"Failed to handle callback query: {e}")
            # Still answer the callback to remove loading state
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    await client.post(
                        f"{self.telegram_api_base}/answerCallbackQuery",
                        json={
                            "callback_query_id": callback_query_id,
                            "text": "Error occurred",
                            "show_alert": True
                        }
                    )
            except:
                pass
            return False
    
    async def _auto_delete_message(self, chat_id: str, message_id: int, delay_seconds: int):
        """Auto-delete message after specified delay (in seconds)"""
        try:
            logger.info(f"⏳⏳⏳ AUTO-DELETE TASK STARTED: message_id={message_id}, chat_id={chat_id}, delay={delay_seconds}s")
            await asyncio.sleep(delay_seconds)
            logger.info(f"⏰⏰⏰ DELAY COMPLETE - Now deleting message {message_id} from chat {chat_id}")
            
            # ✅ CRITICAL: Use JSON format for deleteMessage (Telegram Bot API requirement)
            async with httpx.AsyncClient(timeout=10.0) as client:
                delete_url = f"{self.telegram_api_base}/deleteMessage"
                delete_payload = {
                    "chat_id": str(chat_id),  # ✅ Ensure string
                    "message_id": int(message_id)  # ✅ Ensure integer
                }
                
                logger.info(f"🗑️ Calling deleteMessage: {delete_url}, payload={delete_payload}")
                response = await client.post(
                    delete_url,
                    json=delete_payload  # ✅ Use json= not data=
                )
                
                logger.info(f"📥 Delete response: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    logger.info(f"✅✅✅ SUCCESS: Auto-deleted balance message {message_id} from chat {chat_id}, response={response_data}")
                else:
                    response_text = response.text if hasattr(response, 'text') else 'N/A'
                    response_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    logger.error(f"❌❌❌ FAILED to auto-delete message {message_id}: HTTP {response.status_code}, response={response_data}, text={response_text}")
        except Exception as e:
            logger.error(f"❌❌❌ EXCEPTION in auto-delete for message {message_id}: {e}", exc_info=True)