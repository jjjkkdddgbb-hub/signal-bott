import { Client, GatewayIntentBits } from 'discord.js';

const token = process.env.DISCORD_TOKEN;
if (!token) throw new Error('DISCORD_TOKEN غير موجود في متغيرات البيئة');

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] });

async function handleMessage(message) {
  if (message.author.bot) return;
  const reply = await buildReply(message.content);
  await message.reply(reply);
}

client.on('messageCreate', (message) => {
  handleMessage(message).catch((err) => console.error('فشل الرد:', err));
});

try {
  await client.login(token);
} catch (err) {
  console.error('تعذّر تسجيل الدخول إلى البوت:', err.message);
}