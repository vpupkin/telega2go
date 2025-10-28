#!/usr/bin/env node
/**
 * Example Node.js client for OTP Social Gateway
 */

const axios = require('axios');

class OTPGatewayClient {
  constructor(baseUrl = 'http://localhost:55155') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Send OTP to Telegram user
   */
  async sendOTP(chatId, otp, expireSeconds = 30) {
    try {
      const response = await axios.post(`${this.baseUrl}/send-otp`, {
        chat_id: chatId,
        otp: otp,
        expire_seconds: expireSeconds
      });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Check service health
   */
  async healthCheck() {
    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      return {
        status: 'error',
        error: error.message
      };
    }
  }

  /**
   * Get Prometheus metrics
   */
  async getMetrics() {
    try {
      const response = await axios.get(`${this.baseUrl}/metrics`);
      return response.data;
    } catch (error) {
      return `Error: ${error.message}`;
    }
  }

  /**
   * Generate random OTP
   */
  static generateOTP(length = 6) {
    return Array.from({ length }, () => Math.floor(Math.random() * 10)).join('');
  }
}

/**
 * Example usage
 */
async function main() {
  const client = new OTPGatewayClient('http://localhost:55155');

  // Check health
  console.log('Checking service health...');
  const health = await client.healthCheck();
  console.log('Health:', health, '\n');

  if (health.status !== 'ok') {
    console.error('❌ Service is not healthy!');
    process.exit(1);
  }

  // Get chat ID from command line or use default
  const chatId = process.argv[2] || '123456789';

  // Generate and send OTP
  const otp = OTPGatewayClient.generateOTP(6);
  console.log(`Sending OTP ${otp} to chat_id ${chatId}...`);

  const result = await client.sendOTP(chatId, otp, 30);

  if (result.success) {
    console.log('✅ OTP sent successfully!');
    console.log(`   Message ID: ${result.message_id}`);
    console.log(`   Sent at: ${result.sent_at}`);
    console.log(`   Will delete at: ${result.delete_at}`);
  } else {
    console.error(`❌ Failed to send OTP: ${result.error}`);
  }

  // Show metrics
  console.log('\n' + '='.repeat(60));
  console.log('Metrics:');
  console.log('='.repeat(60));
  const metrics = await client.getMetrics();
  const lines = metrics.split('\n');
  lines.forEach(line => {
    if (line.startsWith('otp_') || line.startsWith('rate_limit_')) {
      console.log(line);
    }
  });
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = OTPGatewayClient;