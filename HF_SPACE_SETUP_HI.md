# Hugging Face ZeroGPU Space — मोबाइल से स्थापना

## तैयार फाइलें
`hf-space/app.py`, `hf-space/requirements.txt`, `hf-space/README.md`

## मोबाइल पर कदम
1. Chrome में Hugging Face खोलकर अपने खाते में sign in करें।
2. Create → New Space चुनें।
3. नाम रखें: `gbsbforyou-hindi-voice`
4. SDK में Gradio चुनें।
5. Visibility चुनें। निजी आवाज़ के परीक्षण के लिए उपलब्ध हो तो Private बेहतर है।
6. Space बन जाने पर Files में ऊपर दी गई तीनों फाइलें root में अपलोड करें। फ़ोल्डर `hf-space` को जस का तस upload न करें; उसके अंदर की फाइलें Space root में रखें।
7. Settings → Hardware में ZeroGPU चुनें, यदि विकल्प उपलब्ध हो।
8. Build पूरा होने तक Logs देखें।
9. Space खुलने पर 15–30 सेकंड की साफ अपनी रिकॉर्डिंग और छोटा हिंदी वाक्य डालकर परीक्षण करें।

## लागत और सीमा
Hugging Face की वर्तमान ZeroGPU दस्तावेज़ के अनुसार free personal account पर पात्र खातों को अधिकतम 2 ZeroGPU Spaces मिल सकते हैं। Free account की दैनिक GPU quota सीमित है (दस्तावेज़ में 5 मिनट प्रतिदिन)। इसलिए यह केवल prototype/test के लिए है, नियमित उत्पादन उपयोग के लिए नहीं।

Paid dedicated GPU Spaces की कीमत hardware के अनुसार प्रति घंटे लगती है। GPU चालू रहने पर idle समय भी bill हो सकता है; काम के बाद Space को pause या CPU Basic पर बदलें।

## महत्वपूर्ण
यह ZeroGPU Gradio Space है। हमारे V2.2 frontend का वर्तमान API contract FastAPI `/api/voice-clone` है, इसलिए यह Gradio demo सीधे V2.2 के Backend URL में नहीं डाला जा सकता। पहले ZeroGPU पर आवाज़ की गुणवत्ता जाँचेंगे; उसके बाद Gradio API integration या अलग FastAPI GPU hosting का निर्णय होगा।
