# 🛡️ SentriGate AI

### AI-Powered API Gateway & Security Platform

SentriGate AI is an intelligent API Gateway platform designed to protect backend APIs from unauthorized access, excessive traffic, suspicious requests, and abnormal API behavior.

It combines **JWT authentication, API key management, Redis-based rate limiting, request validation, audit logging, and ML-based threat detection** into a centralized security layer.

---

## 🚀 Features

- 🔐 **JWT Authentication**
- 🔑 **API Key Management**
- ⚡ **Redis-based Rate Limiting**
- 🤖 **ML-based Threat Detection**
- 🛡️ **Request Validation**
- 📊 **Audit Logging**
- 👥 **Role & Permission Management**
- 🚨 **Suspicious Request Detection**
- 📈 **API Usage Monitoring**
- 🐳 **Docker Support**
- 📚 **Interactive Swagger API Documentation**

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      API Client     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SentriGate AI     │
                    │    API Gateway      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌────────────┐   ┌──────────────┐
        │    JWT    │    │ API Keys   │   │ Rate Limiter │
        │   Auth    │    │ Management │   │    Redis     │
        └─────┬─────┘    └──────┬─────┘   └──────┬───────┘
              │                 │                │
              └─────────────────┼────────────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Request Validation  │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Threat Detection ML │
                     └──────────┬──────────┘
                                │
                         ┌──────┴──────┐
                         │             │
                       ALLOW          BLOCK
                         │             │
                         ▼             ▼
                  ┌────────────┐   ┌─────────┐
                  │ Backend /  │   │ Security│
                  │ Protected  │   │  Logs   │
                  │    APIs    │   └─────────┘
                  └────────────┘

