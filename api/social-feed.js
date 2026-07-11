import fetch from 'node-fetch';

export default async function handler(req, res) {
  // تفعيل بروتوكولات الحماية والوصول المباشر للواجهات
  res.setHeader('Access-Control-Allow-Origin', '*'); 
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  // البيانات الاحترافية البديلة للمؤسس في حال الطوارئ أو توقف خدمات الـ APIs العالمية
  const fallbackFeeds = [
    { source: "x", type: "Post", timestamp: "2026-07-10", content: "نعمل حالياً على ضبط خوارزميات الذكاء الاصطناعي الجزيئي في منصة VITO لزيادة دقة تحسين الصيغ العطرية بنسبة تتجاوز 40%.", url: "https://x.com/Mhh1430" },
    { source: "linkedin", type: "Share", timestamp: "2026-07-08", content: "سعيد بنشر ورقة بحثية مصغرة تستعرض مراحل التفرد الثلاث عبر أطروحة حد آينكس (The Ainex Limit). شكراً لكل الباحثين المهتمين.", url: "https://www.linkedin.com/in/mahdi-h-al-hajji-b188703a9/" },
    { source: "github", type: "Release", timestamp: "2026-07-05", content: "تم إطلاق تحديث آمن لمستودع محرك Nex Shield Engine لمنع كشط النماذج اللغوية الضخمة على شبكات Edge.", url: "https://github.com/mhh1430hacker" }
  ];

  let aggregatedItems = [];

  // 1. استدعاء البيانات من مستودع GitHub الخاص بك بأمان عالي وتحت الكاش المفتاحي المرفوع في Vercel
  try {
    const githubToken = process.env.GITHUB_TOKEN;
    const headers = githubToken ? { 'Authorization': `token ${githubToken}` } : {};
    const githubRes = await fetch('https://api.github.com/users/mhh1430hacker/events/public', { headers, timeout: 3000 });
    
    if (githubRes.ok) {
      const events = await githubRes.json();
      events.slice(0, 3).forEach(event => {
        aggregatedItems.push({
          source: "github",
          type: event.type.replace("Event", ""),
          timestamp: event.created_at.slice(0, 10),
          content: `مستودع: ${event.repo.name} — نشاط برمي جديد.`,
          url: `https://github.com/${event.repo.name}`
        });
      });
    }
  } catch (e) { console.error("GitHub Connection Refused", e); }

  // 2. استدعاء التغريدات الحية من حسابك في X عبر الـ Bearer Token المرفوع في إعدادات البيئة
  try {
    const xToken = process.env.TWITTER_BEARER_TOKEN;
    if (xToken) {
      const xRes = await fetch('https://api.twitter.com/2/users/by/username/Mhh1430', {
        headers: { 'Authorization': `Bearer ${xToken}` }
      });
      if (xRes.ok) {
        const userData = await xRes.json();
        const userId = userData.data.id;
        const tweetsRes = await fetch(`https://api.twitter.com/2/users/${userId}/tweets?max_results=5`, {
          headers: { 'Authorization': `Bearer ${xToken}` }
        });
        if (tweetsRes.ok) {
          const tweetsData = await tweetsRes.json();
          const tweets = tweetsData.data || [];
          tweets.slice(0, 2).forEach(t => {
            aggregatedItems.push({
              source: "x",
              type: "Post",
              timestamp: "مؤخراً",
              content: t.text,
              url: "https://x.com/Mhh1430"
            });
          });
        }
      }
    }
  } catch (e) { console.error("X Telemetry Connection Failed", e); }

  // في حال خلو المصفوفة من البيانات الحية بسبب خطأ شبكة خارجي، يتم دمج البيانات الاحتياطية تلقائياً ليبقى الموقع جذاباً وثابتاً
  if (aggregatedItems.length === 0) {
    aggregatedItems = fallbackFeeds;
  }

  // تفعيل التخزين المؤقت الذكي على خوادم الـ Edge لشركة Vercel لمدة 15 دقيقة لتوفير سرعة تحميل خارقة وحماية خوادمك
  res.setHeader('Cache-Control', 's-maxage=900, stale-while-revalidate');
  return res.status(200).json(aggregatedItems);
}
