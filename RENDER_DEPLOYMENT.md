# Render Deployment Guide

## Quick Setup

1. **Connect your repository** to Render
2. **Create a new Web Service** in Render dashboard
3. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
   - **Python Version:** 3.12.0 (or use runtime.txt)

## Important Notes

### PORT Environment Variable
- Render automatically sets the `PORT` environment variable
- The app is configured to read `PORT` from the environment
- Do NOT set PORT manually in Render's environment variables

### Environment Variables (Optional)
You can set these in Render's dashboard:
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: *)

### Troubleshooting

**Issue: App not starting**
- Check that `requirements.txt` includes `-e .` to install the local package
- Verify Python version matches runtime.txt (3.12.0)
- Check build logs for import errors

**Issue: Port binding errors**
- Ensure start command uses `$PORT` (Render's environment variable)
- Don't hardcode port numbers

**Issue: Import errors**
- Make sure `pyOfferUp` package is installed via `-e .` in requirements.txt
- Verify all dependencies are in requirements.txt

**Issue: Different results than local**
- Check environment variables match local setup
- Verify the same Python version is used
- Check logs for any errors or warnings

## Testing Deployment

After deployment, test the endpoints:
- Health check: `https://your-app.onrender.com/api/v1/health`
- API docs: `https://your-app.onrender.com/docs`
- Search: `https://your-app.onrender.com/api/v1/cars/search?query=car&state=California&city=Los+Angeles&limit=5`

