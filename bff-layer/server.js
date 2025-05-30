const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const port = process.env.PORT || 3000;

// Proxy middleware
app.use('/api/v1', createProxyMiddleware({
  target: 'http://localhost:5000',
  changeOrigin: true,
}));

// Health check route
app.get('/api/bff/health', (req, res) => {
  res.json({ status: 'BFF is running' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

app.listen(port, () => {
  console.log(`BFF layer listening at http://localhost:${port}`);
});
