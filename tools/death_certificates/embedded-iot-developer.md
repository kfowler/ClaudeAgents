# Death Certificate: embedded-iot-developer

**Agent Name:** embedded-iot-developer
**Date of Creation:** 2024 (mid-year)
**Date of Death:** 2025-10-10
**Lifespan:** ~6-9 months
**Tier:** Extended
**Cause of Death:** Hyper-niche specialization, zero adoption, no demonstrated demand

## Detailed Autopsy

**Symptoms Leading to Death:**
- Hyper-specialized: embedded systems + IoT protocols + edge devices
- Zero command usage across all 68 commands
- Zero documentation references outside CLAUDE.md keyword list
- No user requests or examples involving embedded/IoT development
- Better served by systems-engineer (embedded systems, C/C++, Rust) for most use cases
- IoT is specialized domain requiring hardware expertise beyond software agent scope

**Root Causes:**
- **Premature Specialization**: Created agent before validating embedded/IoT demand from user base
- **Hardware-Software Gap**: Embedded/IoT development requires hardware access, physical testing, device debugging—difficult for AI agent to provide value
- **Niche Market**: Most ClaudeAgents users work on web apps, mobile apps, APIs—not embedded systems
- **Better Generalist**: systems-engineer covers embedded systems programming (C, C++, Rust, performance optimization) without IoT-specific constraints

## Lessons Learned

1. **Hardware Domains Need Special Consideration:** Embedded/IoT development requires physical hardware, oscilloscopes, logic analyzers, JTAG debuggers. AI agents add limited value without physical access.

2. **Validate Market Fit:** Zero adoption in 6+ months signals market mismatch. ClaudeAgents user base primarily does web/mobile/cloud development, not embedded systems.

3. **Community-Driven Niche Agents:** Hyper-specialized domains (embedded, IoT, FPGA, hardware) should emerge from community demand, not speculative platform additions.

## Migration Path

**For users who might have used embedded-iot-developer:**

**Use Case 1: Embedded systems programming (C, C++, Rust, bare metal)**
→ **Replacement:** `systems-engineer`
→ **Why:** Deep expertise in low-level programming, memory management, performance optimization, systems programming languages (C, C++, Rust, Go).

**Use Case 2: IoT protocols (MQTT, CoAP, LoRaWAN, Zigbee)**
→ **Replacement:** `backend-api-engineer` or `systems-engineer`
→ **Why:** IoT protocols are network protocols. backend-api-engineer understands protocol design, message queuing, pub/sub patterns. systems-engineer handles low-level protocol implementation.

**Use Case 3: Edge device deployment (Raspberry Pi, Arduino, ESP32)**
→ **Replacement:** `systems-engineer` + `devops-engineer`
→ **Why:** Edge device programming (systems-engineer) + deployment automation (devops-engineer). Covers firmware development and fleet management.

**Use Case 4: IoT cloud integration (AWS IoT, Azure IoT Hub, Google Cloud IoT)**
→ **Replacement:** `cloud-architect` + `backend-api-engineer`
→ **Why:** Cloud IoT platforms are cloud services requiring architecture expertise (cloud-architect) and API integration (backend-api-engineer).

**Use Case 5: Real-time systems, RTOS (FreeRTOS, Zephyr, RT-Thread)**
→ **Replacement:** `systems-engineer`
→ **Why:** Real-time systems require low-level OS knowledge, scheduling, interrupt handling, timing constraints—all systems-engineer expertise.

**Use Case 6: Sensor integration, data acquisition**
→ **Replacement:** `data-engineer` + `systems-engineer`
→ **Why:** Sensor data pipelines (data-engineer) + low-level sensor interfacing (systems-engineer). Covers full stack from hardware to analytics.

**Search Keyword Redirects:**
- "embedded", "bare metal", "C/C++ embedded", "Rust embedded" → `systems-engineer`
- "MQTT", "CoAP", "IoT protocols", "LoRaWAN" → `backend-api-engineer`
- "Raspberry Pi", "Arduino", "ESP32", "edge device" → `systems-engineer`
- "AWS IoT", "Azure IoT Hub", "cloud IoT" → `cloud-architect`
- "RTOS", "FreeRTOS", "real-time systems" → `systems-engineer`
- "sensor data", "data acquisition", "telemetry" → `data-engineer`

## Final Notes

The death of embedded-iot-developer reflects honest platform assessment: this agent was created speculatively without validating user demand.

**Market Reality (2025):**
- ClaudeAgents users primarily develop:
  - Web applications (React, Next.js, Svelte) → full-stack-architect
  - Mobile apps (iOS, Android, React Native) → mobile-developer
  - Backend APIs (REST, GraphQL, microservices) → backend-api-engineer
  - Cloud infrastructure (AWS, Azure, GCP) → cloud-architect, devops-engineer

- Embedded/IoT development is <1% of user requests

**Why Zero Adoption:**
1. **Hardware Barrier**: Embedded development requires physical devices, hardware debugging tools
2. **Niche Market**: Most users building software, not firmware
3. **Generalists Suffice**: systems-engineer handles the rare embedded request effectively

**If Embedded/IoT Demand Emerges:**
- Community contributions should drive it (proven demand)
- Consider creating specialist when demand reaches 5-10% of user requests
- Focus on software aspects (firmware, protocols, cloud integration) where AI agents add value

**Platform gains:**
- **Honest Assessment**: Remove speculative agents with zero adoption
- **Focus on Core**: Invest in agents serving 95%+ of users (web, mobile, API, cloud)
- **Community Path**: Open door for embedded specialist if community demonstrates demand

**Users gain:**
- **No Confusion**: Clear guidance (embedded → systems-engineer)
- **Proven Expertise**: systems-engineer has battle-tested embedded systems knowledge
- **Better Resource Allocation**: Platform focuses on high-demand domains

This deprecation validates: **Create agents for demonstrated demand, not speculative niches. Zero adoption in 6+ months = clear signal.**

---

**Death Certificate prepared by:** product-manager, systems-engineer
**Date:** 2025-10-10
