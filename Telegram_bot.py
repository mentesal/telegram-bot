from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from typing import Final

TOKEN: Final = '7526814127:AAFIwlc7LZPQ3Aid6CtDk1pRVH15fdtccN4'
BOT_USERNAME = '@WKU_delivery_services_bot'

# Define states for conversation flow
PHONE_NUMBER, ORDER_DETAILS = range(2)

# Store orders in memory (for now)
orders = {}

# Define the admin's user ID (Replace with the actual admin ID)
ADMIN_USER_ID = 837089052  # Replace this with your actual Telegram user ID

# Store user's phone numbers temporarily
user_phone_numbers = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message."""
    await update.message.reply_text(
        "ውድ የወልቂጤ ዩንቨርስቲ ተማሪዎች እንኳን ወደ wku delivery service bot በደህና መጡ.\n"
        "1. ለ Foood delivery\n"
        "1.1 Delivery from emet(belay)\n"
        "1.2 Delivery from gebi memihiran\n"
        "1.3 Delivery from gubure mera(ሜራ)\n"
        "1.4 Delivery from gubure sweet\n"
        "1.5 Delivery from gubure ኬር\n"
        "1.6 Delivery from gubure totot\n"
        "1.7 Delivery from gebi sebele (ማሚ)\n"
        "2. ለ Delivery from A.A\n"
        "3. ለ Wash close"
    )


async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user for phone number."""
    keyboard = [[KeyboardButton("📞 Share My Number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Please share your phone number to proceed with your order:",
                                    reply_markup=reply_markup)
    return PHONE_NUMBER  # Move to the next step (waiting for phone number)


async def save_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the user's phone number."""
    contact = update.message.contact
    user_id = update.message.chat_id
    phone_number = contact.phone_number

    # Store the phone number temporarily in user_phone_numbers
    user_phone_numbers[user_id] = phone_number

    # Ask for order details after phone number is shared
    await update.message.reply_text(
        "Thank you! Now, please enter your order details "
        "(e.g., 'Food (beyeaynet, dabo, erteb), from A.A and Packages ') with a place you want."
    )
    return ORDER_DETAILS  # Move to next step (order details)


async def save_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the user's order and send both the order and phone number to the admin."""
    user_id = update.message.chat_id
    order_text = update.message.text
    phone_number = user_phone_numbers.get(user_id, "Unknown")  # Get the phone number from the stored data

    # Store the order in memory
    orders[user_id] = {"order": order_text, "status": "Pending", "phone": phone_number}

    # Send both order and phone number to the admin
    admin_message = f"📦 New Order:\nUser ID: {user_id}\nPhone: {phone_number}\nOrder: {order_text}"
    await context.bot.send_message(chat_id=ADMIN_USER_ID, text=admin_message)

    await update.message.reply_text(f"✅ Order received: {order_text}\nYou can check the status with /track_order.")
    return ConversationHandler.END  # End conversation


async def track_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check order status."""
    user_id = update.message.chat_id

    if user_id in orders:
        order_info = orders[user_id]
        await update.message.reply_text(f"📦 Your order: {order_info['order']}\nStatus: {order_info['status']}")
    else:
        await update.message.reply_text("❌ No order found. Use /order to place one.")


async def orders_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to see all orders."""
    user_id = update.message.chat_id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ You do not have permission to view the orders.")
        return

    if not orders:
        await update.message.reply_text("📭 No orders yet.")
        return

    response = "📋 All Orders:\n"
    for user, data in orders.items():
        response += f"👤 User {user}: {data['order']} - {data['status']} (Phone: {data['phone']})\n"

    await update.message.reply_text(response)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("❌ Order canceled.")
    return ConversationHandler.END


# Initialize bot
app = Application.builder().token(TOKEN).build()

# Conversation handler for ordering
order_handler = ConversationHandler(
    entry_points=[CommandHandler("order", order)],
    states={
        PHONE_NUMBER: [MessageHandler(filters.CONTACT, save_phone)],  # Collect phone number
        ORDER_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_order)],  # Save order details
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(order_handler)
app.add_handler(CommandHandler("track_order", track_order))
app.add_handler(CommandHandler("orders", orders_list))  # Admin command
print("🤖 Bot is running...")
app.run_polling()
