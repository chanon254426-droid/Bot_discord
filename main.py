import discord
from discord.ext import commands
from discord import app_commands # ⬅️ เพิ่มตามรูป (สำหรับ Slash Commands)
from server import server_on # ⬅️ เพิ่มตามรูป (สำหรับ Web Server 24/7)

# =================================================================
# 🛠️ --- ส่วนที่คุณต้องแก้ไข/ใส่ค่า ID และลิงก์ (มี 15 รายการ) --- 🛠️
# =================================================================

TOKEN = 'YOUR_BOT_TOKEN_HERE'  # 🔑 Bot Token ที่ได้จาก Discord Developer Portal
SHOP_CHANNEL_ID = 123456789012345678  # 🛒 ID แชนเนลร้านค้า (ที่ลูกค้าเห็นปุ่มซื้อ)
ADMIN_LOG_CHANNEL_ID = 123456789012345678  # 🔒 ID แชนเนล Log สำหรับแอดมินเท่านั้น (ลูกค้าต้องส่งสลิปในนี้)

# 📣 ข้อมูลยศทั้งหมดที่คุณต้องการขาย (15 รายการ) 📣
SALE_ITEMS = [
    # (รายการยศ 15 รายการของคุณ)
    {
        "role_id": 999000111222333444,
        "name": "Role-01", 
        "price": "100 บาท", 
        "qr_url": 'https://link.to/qr01.png'
    },
    {
        "role_id": 999000111222333555,
        "name": "Role-02", 
        "price": "200 บาท", 
        "qr_url": 'https://link.to/qr02.png'
    },
    {
        "role_id": 999000111222333666,
        "name": "Role-03", 
        "price": "300 บาท", 
        "qr_url": 'https://link.to/qr03.png'
    },
    {
        "role_id": 999000111222333777,
        "name": "Role-04", 
        "price": "400 บาท", 
        "qr_url": 'https://link.to/qr04.png'
    },
    {
        "role_id": 999000111222333888,
        "name": "Role-05", 
        "price": "500 บาท", 
        "qr_url": 'https://link.to/qr05.png'
    },
    {
        "role_id": 999000111222333999,
        "name": "Role-06", 
        "price": "600 บาท", 
        "qr_url": 'https://link.to/qr06.png'
    },
    {
        "role_id": 999000111222444000,
        "name": "Role-07", 
        "price": "700 บาท", 
        "qr_url": 'https://link.to/qr07.png'
    },
    {
        "role_id": 999000111222444111,
        "name": "Role-08", 
        "price": "800 บาท", 
        "qr_url": 'https://link.to/qr08.png'
    },
    {
        "role_id": 999000111222444222,
        "name": "Role-09", 
        "price": "900 บาท", 
        "qr_url": 'https://link.to/qr09.png'
    },
    {
        "role_id": 999000111222444333,
        "name": "Role-10", 
        "price": "1000 บาท", 
        "qr_url": 'https://link.to/qr10.png'
    },
    {
        "role_id": 999000111222444444,
        "name": "Role-11", 
        "price": "1100 บาท", 
        "qr_url": 'https://link.to/qr11.png'
    },
    {
        "role_id": 999000111222444555,
        "name": "Role-12", 
        "price": "1200 บาท", 
        "qr_url": 'https://link.to/qr12.png'
    },
    {
        "role_id": 999000111222444666,
        "name": "Role-13", 
        "price": "1300 บาท", 
        "qr_url": 'https://link.to/qr13.png'
    },
    {
        "role_id": 999000111222444777,
        "name": "Role-14", 
        "price": "1400 บาท", 
        "qr_url": 'https://link.to/qr14.png'
    },
    {
        "role_id": 999000111222444888,
        "name": "Role-15", 
        "price": "1500 บาท", 
        "qr_url": 'https://link.to/qr15.png'
    },
]

# =================================================================
# ⚙️ --- ส่วนการตั้งค่าบอทพื้นฐาน (ไม่ควรแก้ไข) --- ⚙️
# * เนื่องจากคุณใช้ app_commands (Slash Commands) ใน on_ready, ควรใช้ Intents.all() 
# * แต่เนื่องจากโค้ดเดิมใช้ Intents.default() + 2 ตัว, ผมจะคงโค้ดเดิมไว้เพื่อไม่ให้เกิดปัญหา Permission
# =================================================================

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ----------------- View/Button สำหรับการอนุมัติของแอดมิน (ตัดโค้ดซ้ำออก) -----------------
# คลาส ApprovalView ยังคงเดิม
class ApprovalView(discord.ui.View):
    def __init__(self, user_id, role_id, original_message):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.role_id = role_id
        self.original_message = original_message
        
    async def on_timeout(self):
        try:
            await self.original_message.edit(content=f"⚠️ หมดเวลาอนุมัติสำหรับสลิปของ <@{self.user_id}> แล้ว", view=None)
        except:
            pass
            
    async def send_log_to_user(self, member, is_approved):
        log_channel = self.original_message.channel 
        if is_approved:
            await log_channel.send(f"✅ <@{member.id}>: การชำระเงินได้รับการยืนยันแล้ว! ยศ <@&{self.role_id}> ถูกมอบให้แล้ว\n**(จากสลิปข้อความ)** {self.original_message.jump_url}")
        else:
            await log_channel.send(f"❌ <@{member.id}>: สลิปไม่ถูกต้อง/ไม่ชัดเจน กรุณาตรวจสอบและส่งใหม่\n**(จากสลิปข้อความ)** {self.original_message.jump_url}")

    @discord.ui.button(label="✅ ยืนยัน", style=discord.ButtonStyle.success, custom_id="approve_button")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("คุณไม่มีสิทธิ์ในการอนุมัติ!", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.user_id)
        role = guild.get_role(self.role_id)

        if member and role:
            await member.add_roles(role)
            await interaction.response.edit_message(
                content=f"✅ อนุมัติโดย {interaction.user.display_name} | มอบยศ <@&{self.role_id}> ให้กับ <@{self.user_id}> แล้ว", 
                view=None
            )
            await self.send_log_to_user(member, True)
        else:
            await interaction.response.send_message("❌ เกิดข้อผิดพลาด: ไม่พบสมาชิกหรือยศ", ephemeral=True)

    @discord.ui.button(label="❌ หึ", style=discord.ButtonStyle.danger, custom_id="reject_button")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("คุณไม่มีสิทธิ์ในการดำเนินการ!", ephemeral=True)
            return
        
        member = interaction.guild.get_member(self.user_id)
        
        await interaction.response.edit_message(
            content=f"❌ ไม่อนุมัติโดย {interaction.user.display_name} | ปฏิเสธการให้ยศกับ <@{self.user_id}>",
            view=None
        )
        await self.send_log_to_user(member, False)
        
# ----------------- View/Button สำหรับการซื้อของลูกค้า (ตัดโค้ดซ้ำออก) -----------------

class BuyButton(discord.ui.Button):
    def __init__(self, item: dict):
        super().__init__(
            label=f"ซื้อยศ {item['name']} ({item['price']})",
            style=discord.ButtonStyle.primary,
            custom_id=f"buy_role_{item['role_id']}"
        )
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        item = self.item
        embed = discord.Embed(
            title="🛒 รายละเอียดการชำระเงิน",
            description=f"**คุณกำลังจะซื้อยศ:** <@&{item['role_id']}> **ในราคา {item['price']}**\n\nกรุณาชำระเงินและส่งรูปสลิปในแชนเนลส่งสลิปเพื่อรอแอดมินอนุมัติ",
            color=discord.Color.gold()
        )
        embed.set_image(url=item['qr_url']) 
        log_channel = interaction.guild.get_channel(ADMIN_LOG_CHANNEL_ID)
        if log_channel:
            await interaction.response.send_message(
                f"✅ **ส่งสลิปที่นี่:** หลังจากชำระเงินแล้ว กรุณาส่งสลิปในแชนเนล <#{log_channel.id}> เพื่อรอการตรวจสอบและอนุมัติ (ข้อความนี้เห็นแค่คุณคนเดียว)\n\n**⚠️ สำคัญ:** กรุณาพิมพ์ **ชื่อยศ** ที่คุณซื้อ (เช่น `Role-01`) หรือ **ราคา** ในข้อความเดียวกับสลิป เพื่อให้แอดมินอนุมัติได้ง่ายขึ้น", 
                embed=embed, 
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ เกิดข้อผิดพลาดในการตั้งค่าแชนเนล Log กรุณาติดต่อแอดมิน", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, sale_items: list):
        super().__init__(timeout=None)
        for item in sale_items:
            self.add_item(BuyButton(item))

# ----------------- คำสั่งบอทและ Events (ปรับแก้ตามรูป) -----------------

@bot.event
async def on_ready():
    print('Bot Online!') # ⬅️ แก้ไขตามรูปที่ 1
    
    # ส่วนนี้คือการ Sync Slash Commands ตามรูปที่ 1
    try:
        synced = await bot.tree.sync()
        print(f"[{len(synced)}] command(s)") # ⬅️ แก้ไขตามรูปที่ 1
    except Exception as e:
        print(f"Error syncing commands: {e}")
        
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    bot.add_view(ShopView(SALE_ITEMS)) 

# *หมายเหตุ: หากคุณเพิ่ม app_commands เข้ามาแล้ว คุณสามารถสร้าง Slash Command ได้โดยใช้ @bot.tree.command() *

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    """คำสั่งสำหรับแอดมิน เพื่อแสดงหน้าต่างร้านค้า"""
    channel = bot.get_channel(SHOP_CHANNEL_ID)
    if not channel:
        await ctx.send(f"❌ ไม่พบแชนเนลร้านค้า ID: {SHOP_CHANNEL_ID}")
        return
        
    description_list = []
    for item in SALE_ITEMS:
        description_list.append(f"**ยศ {item['name']}** ราคา **{item['price']}**")

    embed = discord.Embed(
        title="🛒 ร้านค้าจำหน่ายยศ",
        description='\n'.join(description_list) + "\n\nกดปุ่มด้านล่างเพื่อทำการสั่งซื้อและรับ QR Code",
        color=discord.Color.blue()
    )
    
    await channel.send(embed=embed, view=ShopView(SALE_ITEMS))
    await ctx.send("✅ ตั้งค่าร้านค้าเสร็จสมบูรณ์!")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    # ตรวจสอบว่าข้อความถูกส่งในแชนเนล Log ที่กำหนดหรือไม่ และเป็นรูปภาพ/สลิปหรือไม่
    if message.channel.id == ADMIN_LOG_CHANNEL_ID and message.attachments and not message.author.bot:
        
        log_channel = bot.get_channel(ADMIN_LOG_CHANNEL_ID)
        if log_channel:
            default_item = SALE_ITEMS[0] 

            log_embed = discord.Embed(
                title="🚨 มีสลิปใหม่รอการอนุมัติ!",
                description=f"**ผู้ซื้อ:** {message.author.mention} (`{message.author.id}`)\n**ข้อความผู้ใช้:** {message.content or 'ไม่มีข้อความ'}\n\n**⚠️ โปรดตรวจสอบสลิปและระบุยศที่ต้องการด้วยตนเอง ⚠️**\n**ยศที่ถูกเสนอ (Default):** <@&{default_item['role_id']}>\n**สลิป:** (ดูรูปด้านล่าง)",
                color=discord.Color.red()
            )
            log_embed.set_image(url=message.attachments[0].url) 
            
            log_message = await log_channel.send(
                content=f"**สลิปใหม่จาก:** {message.author.mention}", 
                embed=log_embed, 
                view=ApprovalView(message.author.id, default_item['role_id'], message) 
            )
            
            await message.channel.send(f"🤖 <@{message.author.id}>: ได้รับสลิปของคุณแล้ว! กรุณารอแอดมินตรวจสอบสักครู่", delete_after=10)
        
    

# รันบอท
if __name__ == '__main__':
    # ⬅️ เพิ่มบรรทัดนี้ตามรูปที่ 2
    server_on() 
    try:
        # ใช้ reconnect=True เพื่อความเสถียร (แนะนำ)
        bot.run(TOKEN, reconnect=True) 
    except Exception as e:
        print(f"An error occurred: {e}")