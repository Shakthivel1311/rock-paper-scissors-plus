# Deploying Rock-Paper-Scissors-Plus to Vercel

## Prerequisites
1. GitHub account
2. Vercel account (sign up at https://vercel.com)
3. Git installed

## Step-by-Step Deployment

### 1. Initialize Git Repository
```bash
cd c:\Users\Shakthivel\OneDrive\Documents\Project_upliance
git init
git add .
git commit -m "Initial commit: Rock-Paper-Scissors-Plus game"
```

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., "rock-paper-scissors-plus")
3. Don't initialize with README (we already have files)

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/rock-paper-scissors-plus.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Vercel

#### Option A: Using Vercel Dashboard (Easiest)
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset:** Other
   - **Build Command:** Leave empty
   - **Output Directory:** Leave empty
4. Add Environment Variable:
   - **Name:** `GOOGLE_API_KEY`
   - **Value:** `AIzaSyDxVFfHfhEz_5WiSqMeiJ-t_n1TRx2QMVw`
5. Click "Deploy"

#### Option B: Using Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Add environment variable
vercel env add GOOGLE_API_KEY
# Paste: AIzaSyDxVFfHfhEz_5WiSqMeiJ-t_n1TRx2QMVw

# Deploy to production
vercel --prod
```

### 5. Your App is Live!
After deployment, Vercel will provide you with a URL like:
`https://rock-paper-scissors-plus.vercel.app`

## Important Notes

⚠️ **API Key Security:**
- Never commit your API key to GitHub
- Use Vercel's environment variables
- After pushing to GitHub, remove the API key from any committed files

⚠️ **Rate Limits:**
- Free tier Google API has rate limits
- Consider implementing caching or using a paid plan for production

## Files Required for Vercel
- ✅ `app.py` - Main Flask application
- ✅ `game_state.py` - Game logic
- ✅ `requirements.txt` - Python dependencies
- ✅ `vercel.json` - Vercel configuration
- ✅ `templates/index.html` - Frontend

## Troubleshooting

### Issue: "Module not found"
- Make sure `requirements.txt` lists all dependencies
- Redeploy the application

### Issue: "API key not working"
- Check environment variables in Vercel dashboard
- Make sure variable name is exactly `GOOGLE_API_KEY`

### Issue: "Internal Server Error"
- Check Vercel function logs
- Verify all files are pushed to GitHub

## Local Testing Before Deploy
```bash
# Set environment variable
$env:GOOGLE_API_KEY="AIzaSyDxVFfHfhEz_5WiSqMeiJ-t_n1TRx2QMVw"

# Run locally
.venv\Scripts\python app.py

# Visit: http://localhost:5000
```

## After Deployment
1. Test the live URL
2. Share with others!
3. Monitor usage in Vercel dashboard
4. Check Google AI API usage at https://ai.dev/rate-limit

---

**Your game will be live and accessible to anyone with the URL!** 🚀
