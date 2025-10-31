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
    
    def _init_translations(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Initialize multi-language translations for menu and responses"""
        return {
            "en": {
                "menu": {
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
                "menu": {
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
                "menu": {
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
        """Get translated menu text for an action"""
        lang = self._get_language(language_code)
        return self.translations[lang]["menu"][action_key][field]
    
    def _get_response_text(self, action_key: str, language_code: Optional[str] = None) -> str:
        """Get translated response text for an action"""
        lang = self._get_language(language_code)
        return self.translations[lang]["menu"][action_key]["response"]
    
    async def handle_inline_query(self, inline_query_id: str, query: str, user_id: str, language_code: Optional[str] = None) -> bool:
        """Handle inline queries when @taxoin_bot (or any bot username) is mentioned in any chat"""
        try:
            # Get user language (default to 'en' if not provided or not supported)
            lang = self._get_language(language_code)
            logger.info(f"Handling inline query for user {user_id} with language: {lang}")
            
            # Define menu action keys
            menu_action_keys = [
                ("1", "joinToMe"),
                ("2", "explainWhatIsThis"),
                ("3", "whatIsMyBalance"),
                ("4", "showLastactions")
            ]
            
            # Build inline query results with translations
            results = []
            for action_id, action_key in menu_action_keys:
                # Get translated texts for this action
                title = self._get_menu_text(action_key, language_code, "title")
                description = self._get_menu_text(action_key, language_code, "description")
                button_text = self._get_menu_text(action_key, language_code, "button")
                initial_message = self._get_menu_text(action_key, language_code, "initial")
                
                # Map action_key to callback_data
                callback_data_map = {
                    "joinToMe": "action_joinToMe",
                    "explainWhatIsThis": "action_explainWhatIsThis",
                    "whatIsMyBalance": "action_whatIsMyBalance",
                    "showLastactions": "action_showLastactions"
                }
                
                # Create inline keyboard with button that will appear in the sent message
                keyboard = [[{
                    "text": button_text,
                    "callback_data": callback_data_map[action_key]
                }]]
                
                result = {
                    "type": "article",
                    "id": action_id,
                    "title": title,
                    "description": description,
                    "input_message_content": {
                        "message_text": initial_message,
                        "parse_mode": "HTML"
                    },
                    "reply_markup": {
                        "inline_keyboard": keyboard
                    }
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
    
    async def handle_callback_query(self, callback_query_id: str, chat_id: str, message_id: int, callback_data: str, language_code: Optional[str] = None) -> bool:
        """Handle callback queries when menu buttons are pressed - posts answer into chat"""
        try:
            # Get user language (default to 'en' if not provided or not supported)
            lang = self._get_language(language_code)
            logger.info(f"Handling callback query '{callback_data}' for chat {chat_id} with language: {lang}")
            
            # Map callback_data to action_key
            action_key_map = {
                "action_joinToMe": "joinToMe",
                "action_explainWhatIsThis": "explainWhatIsThis",
                "action_whatIsMyBalance": "whatIsMyBalance",
                "action_showLastactions": "showLastactions"
            }
            
            # Get action key
            action_key = action_key_map.get(callback_data)
            
            if action_key:
                # Get translated response text
                response_text = self._get_response_text(action_key, language_code)
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