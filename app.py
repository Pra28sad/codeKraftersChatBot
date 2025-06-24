from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching

OPENROUTER_API_KEY = "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"
# OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Minimal company info - just enough for context
COMPANY_INFO = """
CodeKrafters is a leading IT services company based in India. We specialize in:

- Web Development (Custom websites, E-commerce solutions, Web applications)
- Mobile App Development (Android & iOS) 
- Digital Marketing (SEO, Social Media Marketing, Content Marketing)
- UI/UX Design
- Software Development
- Cloud Solutions
- IT Consulting

Our Project Portfolio:

Web Development:
- E-commerce Solutions: Custom e-commerce platforms with secure payment integration, inventory management, and user-friendly interfaces
- Enterprise Applications: Scalable business applications with robust backend systems and intuitive admin dashboards
- Content Management Systems: Customized CMS solutions for efficient content management and website updates

Mobile Development:
- iOS Applications: Native iOS apps with modern UI/UX and seamless performance
- Android Applications: Feature-rich Android apps optimized for various devices
- Cross-platform Solutions: Unified applications that work seamlessly across iOS and Android platforms

Cloud Solutions:
- Cloud Migration: Seamless migration of existing systems to cloud infrastructure
- Cloud-native Applications: Modern applications built specifically for cloud deployment

Leadership:
Sonam Jain - CEO & Founder (10+ years experience in software development and digital transformation)

Development Team:
Skilled developers specializing in various technologies and frameworks.
"""

# Separate contact information
CONTACT_INFO = """
📍 Address: 110, Option Primo, MIDC, Andheri East, Mumbai - 400069
📞 Phone: +91 760 303 2300
📧 Email: virtuoso.sonam@gmail.com
💼 Work Mode: We Work Offline Since Covid
"""

JENNIFER_PROMPT = """
You are Jennifer, a friendly AI assistant at CodeKrafters, with deep expertise in enterprise software solutions and modern digital applications. Keep responses concise and focused only on what is asked.

Important: You should only answer questions related to the CodeKrafters website and its services. If a user asks any question unrelated to this website, politely respond with: "Sorry, I'm only here to assist with questions related to this CodeKrafters website."

📝 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 𝗙𝗼𝗿𝗺𝗮𝘁𝘁𝗶𝗻𝗴 𝗚𝘂𝗶𝗱𝗲𝗹𝗶𝗻𝗲𝘀:

1. Text Styling:
   • Use **bold** for important keywords and key features
   • Use *italics* for emphasis on specific terms
   • Use `code blocks` for technical terms
   • Use emojis strategically for visual breaks

2. Response Structure:
   • Start with a clear heading
   • Use bullet points (•) for lists
   • Use numbered lists (1., 2., 3.) for steps
   • Add line breaks between sections
   • Use horizontal rules (---) to separate major sections

3. Information Organization:
   • Group related information
   • Use subheadings for different topics
   • Maintain consistent spacing
   • Use indentation for hierarchy

Example Response Format:
```
📌 [Main Topic]

• **Key Point 1**
  - Detail 1
  - Detail 2

• **Key Point 2**
  - Detail 1
  - Detail 2

---

🔍 [Sub-topic]

1. First step
2. Second step
3. Third step

---

💡 **Important Note**: [Highlighted information]
```

📝 𝗖𝗮𝘀𝘂𝗮𝗹 𝗖𝗼𝗻𝘃𝗲𝗿𝘀𝗮𝘁𝗶𝗼𝗻 𝗛𝗮𝗻𝗱𝗹𝗶𝗻𝗴:
• For greetings (hi, hello, how are you):
  - Respond warmly but briefly
  - Quickly guide toward business purpose
  - Example: 
    ```
    👋 **Hello!** 
    
    I'm here to help you explore our **services** and **products**. 
    What would you like to know about?
    ```

• For casual questions (what are you doing, how's your day):
  - Keep responses friendly but focused
  - Redirect to business context
  - Example:
    ```
    😊 **I'm here to assist you!**
    
    Would you like to know about:
    • Our **ERP solutions**
    • Our **digital applications**
    • Our **industry-specific systems**
    ```

• For general chitchat:
  - Acknowledge briefly
  - Guide toward specific inquiries
  - Example:
    ```
    💭 **That's interesting!**
    
    While I'm happy to chat, I'm specifically here to help with:
    • **Services** - ERP and management systems
    • **Products** - Digital applications and solutions
    
    What would you like to explore?
    ```

📋 𝗖𝗼𝗿𝗲 𝗘𝘅𝗽𝗲𝗿𝘁𝗶𝘀𝗲:

1. Core ERP-Based Management Systems:
   - Inventory Management System (IMS)
   - Purchase Management System
   - Sales & CRM Management System
   - Production & Manufacturing Management
   - Finance & Accounting Management
   - Supply Chain Management (SCM)
   - Human Resource Management System (HRMS)
   - Project & Task Management System (PMS)
   - Document Management System (DMS)
   - Risk & Compliance Management
   - Sustainability & ESG Management
   - Customer Service & Support Management
   - Facility & Asset Management
   - Logistics & Fleet Management
   - Quality Management System (QMS)
   - Event & Conference Management

2. Industry-Specific ERP Systems:
   Education Sector:
   - School Management System (SMS)
   - University ERP
   - Learning Management System (LMS)
   - EdTech Platform Management

   Healthcare Sector:
   - Hospital Management System (HMS)
   - Clinic & Pharmacy Management
   - Telehealth & Remote Consultation
   - Health Insurance & Claims Management

   Manufacturing & Retail:
   - Production & MRP System
   - Retail ERP
   - Warehouse Management System (WMS)
   - E-commerce & Marketplace Management
   - Franchise Management System
   - Optical Store Management

   Financial & Trading:
   - Option Chain Analysis System
   - Portfolio & Investment Management
   - Loan & Mortgage Management
   - Cryptocurrency & Blockchain Management

   Real Estate & Construction:
   - Pyramid Model ERP
   - Property Listing & Rental Management
   - Interior Design & Architectural Planning
   - Facility & Property Maintenance Management

   Logistics & Delivery:
   - Fleet & Transport Management
   - Delivery Boy Management System
   - Cold Chain Logistics Management
   - Freight & Cargo Management

3. Web 2.0 & 2.5 Apps:
   - E-Commerce Apps
   - Subscription-Based Business Apps
   - Delivery Apps
   - Salon & Spa Booking Apps
   - Car Rental & Ride-Hailing Apps
   - Co-working Space Management
   - Healthcare Teleconsultation Apps
   - AI Chatbot & Virtual Assistant Apps
   - IoT-Based Smart Home Management
   - Metaverse & Virtual Shopping Apps
   - Legal Case Management System
   - NGO & Charity Management System

ℹ️ 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻 𝗦𝗵𝗮𝗿𝗶𝗻𝗴:
• When asked about services:
  ```
  📊 **Service Overview**
  
  • **Category**: [Service Category]
  • **Key Features**:
    - Feature 1
    - Feature 2
  • **Benefits**:
    - Benefit 1
    - Benefit 2
  ```

• When asked about products:
  ```
  🛍️ **Product Details**
  
  • **Product Name**: [Name]
  • **Key Features**:
    - Feature 1
    - Feature 2
  • **Contact Information**:
    - CEO: [Details]
    - Development Team: [Details]
  ```

🎯 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 𝗙𝗼𝗿𝗺𝗮𝘁𝘁𝗶𝗻𝗴:
• Service Inquiries:
  ```
  🔧 **Service Information**
  
  1. **Category**: [Category Name]
  2. **Features**:
     • Feature 1
     • Feature 2
  3. **Benefits**:
     • Benefit 1
     • Benefit 2
  ```

• Product Inquiries:
  ```
  📱 **Product Overview**
  
  1. **Product Name**: [Name]
  2. **Key Features**:
     • Feature 1
     • Feature 2
  3. **Next Steps**:
     • Contact: [Details]
     • Schedule: [Information]
  ```

Key Directive: 
1. For casual conversations:
   - Keep responses brief and friendly
   - Always guide users toward specific service or product inquiries
   - Use phrases like "I'm here to help you with..." or "Would you like to know about..."
   - Format responses with clear structure and highlighting
   - If the user frequently sending casual messages, then divert the topic to the business purpose.
   

2. For business inquiries:
   - Provide detailed, structured information
   - Focus on the specific service or product asked about
   - Include relevant contact information when appropriate
   - Use consistent formatting and highlighting

3. General guidelines:
   - Maintain professional yet friendly tone
   - Use markdown formatting and emojis appropriately
   - Keep responses focused on business purpose
   - Always guide users toward specific inquiries if they're being too casual
   - Ensure all responses are well-organized and easy to read
   - Highlight important keywords and information
   - Use proper spacing and line breaks for readability
   - Always response will have in very well organized manner.
   
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        project_product_count = request.json.get("project_product_count", 0)
        logger.debug(f"Received message: {user_message}, project_product_count: {project_product_count}")

        if not user_message:
            return jsonify({"reply": "Hey! I didn't catch that. Mind trying again? 😊"}), 400

        # Detect if the message is about projects or products
        project_product_keywords = ['project', 'projects', 'product', 'products', 'development', 'software', 'app', 'application', 'website', 'web', 'mobile', 'system', 'solution']
        is_project_product_query = any(keyword in user_message.lower() for keyword in project_product_keywords)

        # Increment count if current message is about projects/products
        if is_project_product_query:
            project_product_count += 1
            logger.debug(f"Incremented project_product_count to {project_product_count}")
        else:
            project_product_count = 0  # reset count if different topic
            logger.debug("Reset project_product_count to 0 due to different topic")

        # If user has asked about projects/products more than 3 times, provide contact info directly
        if project_product_count >= 3:
            logger.debug("project_product_count >= 3, sending contact info")
            contact_info_text = """
# 🎯 **Welcome to CodeKrafters!**

I notice you have a strong interest in our projects and products! Let me provide you with comprehensive information about our services.

---

## 📊 **Our Expertise & Solutions**

### 1. **Web Development** 🌐
   • **Custom Websites**
     - Modern UI/UX Design
     - Responsive Layouts
     - SEO Optimization
   
   • **E-commerce Solutions**
     - Secure Payment Gateways
     - Inventory Management
     - Order Processing
   
   • **Web Applications**
     - Robust Backend Systems
     - API Integration
     - Real-time Features

### 2. **Mobile Development** 📱
   • **Native Applications**
     - iOS Development
     - Android Development
     - Platform-specific Features
   
   • **Cross-platform Solutions**
     - React Native
     - Flutter
     - Hybrid Apps

### 3. **Enterprise Solutions** 💼
   • **Business Applications**
     - ERP Systems
     - CRM Solutions
     - Workflow Automation
   
   • **Cloud Services**
     - Cloud Migration
     - Infrastructure Setup
     - Data Analytics

---

## 📞 **Get in Touch**

### **Contact Details** 📱
   • **Phone**: +91 760 303 2300
   • **Email**: virtuoso.sonam@gmail.com
   • **Response Time**: Within 24 hours

### **Office Location** 📍
   110, Option Primo, MIDC, Andheri East, Mumbai - 400069

---

## 💼 **Our Service Process**

### 1. **Initial Consultation** 📋
   • **Requirements Gathering**
   • **Project Scope Definition**
   • **Technology Stack Selection**
   • **Timeline Estimation**
   • **Cost Analysis**

### 2. **Development Phase** ⚙️
   • **Custom Solution Development**
   • **Third-party Integrations**
   • **API Development**
   • **Database Design**
   • **Security Implementation**

### 3. **Support & Maintenance** 🔧
   • **Regular Updates**
   • **Performance Optimization**
   • **Security Patches**
   • **Technical Support**
   • **Training & Documentation**

---

## 💡 **Key Information**

### **Service Highlights** ⭐
   • **Work Mode**: Offline since Covid
   • **Consultation**: Free initial consultation
   • **Response Time**: Within 24 hours
   • **Support**: 24/7 technical support
   • **Documentation**: Comprehensive guides
   • **Training**: End-user training

---

## 🎯 **Next Steps**

1. **Contact Us**
   - Call or email our team
   - Share your requirements
   - Get immediate response

2. **Consultation**
   - Schedule free meeting
   - Discuss project details
   - Get expert advice

3. **Project Start**
   - Receive proposal
   - Finalize requirements
   - Begin development

---

> 💬 **Ready to Start Your Project?**
> 
> Our expert team is ready to help you bring your ideas to life.
> Contact us today to begin your journey! 😊

"""
            return jsonify({"reply": contact_info_text, "project_product_count": project_product_count})

        # If it's a project/product query but not yet at 3 times, include a hint about contacting
        if is_project_product_query and project_product_count == 2:
            # Add a hint about contacting in the system message
            system_message = f"{JENNIFER_PROMPT}\nCurrent time in India: {current_time}\n\nNote: If the user asks about projects/products again, provide a well-organized response with clear headings, nested bullet points, and highlighted important information. Use horizontal rules to separate sections and add relevant emojis for visual appeal. Include comprehensive contact information with our expertise areas, free consultation, and quick response time."

        # If it's the first project/product query, provide a more detailed initial response
        if is_project_product_query and project_product_count == 1:
            system_message = f"{JENNIFER_PROMPT}\nCurrent time in India: {current_time}\n\nNote: Provide a well-structured response with clear headings and nested bullet points. Use horizontal rules to separate sections and add relevant emojis for visual appeal. Include detailed information about our projects and products, highlight our expertise areas in bold, and mention that we can provide more specific information and a free consultation if they contact our team directly."

        # Check if the question is unrelated to the website/company
        unrelated_keywords = [
            "weather", "news", "sports", "movie", "music", "game", "joke", "recipe",
            "politics", "celebrity", "random", "outside", "external", "outside website",
            "not related", "unrelated", "general knowledge", "fun", "chat", "conversation"
        ]
        if any(keyword in user_message.lower() for keyword in unrelated_keywords):
            return jsonify({"reply": "Sorry, I'm only here to assist with questions related to this CodeKrafters website.", "project_product_count": project_product_count})

        # Get current time in India
        india_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(india_tz).strftime("%I:%M %p")

        # Check if message is asking for contact information
        contact_keywords = ['contact', 'email', 'phone', 'address', 'location', 'reach', 'connect', 'meet', 'office']
        should_include_contact = any(keyword in user_message.lower() for keyword in contact_keywords)

        # Prepare company information based on query
        info_to_use = COMPANY_INFO
        if should_include_contact:
            info_to_use = f"{COMPANY_INFO}\n\nContact Information:\n{CONTACT_INFO}"

        # Add real-time context to the system message
        system_message = f"{JENNIFER_PROMPT}\nCurrent time in India: {current_time}"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": info_to_use},
            {"role": "user", "content": user_message}
        ]

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://codekrafters.in/",
            "X-Title": "Jennifer - CodeKrafters AI Assistant",
            "Content-Type": "application/json",
        }

        data = {
            # "model": "openchat/openchat-3.5",
            "model": "google/gemma-7b-it",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 400,
            "top_p": 0.9,
            "frequency_penalty": 0.6,
            "presence_penalty": 0.7
        }

        logger.debug("Making request to OpenRouter API...")
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response content: {response.text}")

            if response.status_code == 200:
                result = response.json()
                bot_reply = result['choices'][0]['message']['content']
                return jsonify({"reply": bot_reply, "project_product_count": project_product_count})
            elif response.status_code == 401:
                logger.error(f"API Key Error: {response.text}")
                return jsonify({"reply": "I'm having trouble accessing my knowledge base. Please contact support! 🔧", "project_product_count": project_product_count}), 401
            elif response.status_code == 429:
                logger.error(f"Rate Limit Error: {response.text}")
                return jsonify({"reply": "I'm a bit overwhelmed with requests right now. Could you try again in a moment? 😅", "project_product_count": project_product_count}), 429
            else:
                error_message = "I'm having some technical difficulties. Let me get that fixed! 🛠️"
                try:
                    error_detail = response.json()
                    logger.error(f"API Error: {error_detail}")
                except:
                    logger.error(f"API Error: {response.text}")
                return jsonify({"reply": error_message, "project_product_count": project_product_count}), 500

        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return jsonify({"reply": "Sorry for keeping you waiting! Our systems are being a bit slow. Could you try again? ⏳", "project_product_count": project_product_count}), 504
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return jsonify({"reply": "I'm having trouble connecting to my brain. Give me a moment! 🔄", "project_product_count": project_product_count}), 503

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"reply": "Oops! Something unexpected happened. Let me sort that out! 🔧", "project_product_count": project_product_count}), 500

if __name__ == "__main__":
    app.run(debug=True)














# Minimal company info - just enough for context
COMPANY_INFO = """
CodeKrafters is a leading IT services company based in India. We specialize in:

- Web Development (Custom websites, E-commerce solutions, Web applications)
- Mobile App Development (Android & iOS) 
- Digital Marketing (SEO, Social Media Marketing, Content Marketing)
- UI/UX Design
- Software Development
- Cloud Solutions
- IT Consulting

Our Project Portfolio:

Web Development:
- E-commerce Solutions: Custom e-commerce platforms with secure payment integration, inventory management, and user-friendly interfaces
- Enterprise Applications: Scalable business applications with robust backend systems and intuitive admin dashboards
- Content Management Systems: Customized CMS solutions for efficient content management and website updates

Mobile Development:
- iOS Applications: Native iOS apps with modern UI/UX and seamless performance
- Android Applications: Feature-rich Android apps optimized for various devices
- Cross-platform Solutions: Unified applications that work seamlessly across iOS and Android platforms

Cloud Solutions:
- Cloud Migration: Seamless migration of existing systems to cloud infrastructure
- Cloud-native Applications: Modern applications built specifically for cloud deployment

We are committed to delivering innovative digital solutions that help businesses grow and succeed in the digital world. Our team of experienced developers and digital marketing experts work together to provide end-to-end solutions for our clients.

Our Leadership:
Sonam Jain - CEO & Founder
Leading our talented team at CodeKrafters with over 10 years of industry experience in software development and digital transformation. Under her visionary leadership, we've successfully delivered numerous innovative solutions to clients worldwide.

Our Development Team:
We have a strong team of skilled developers specializing in various technologies and frameworks. Our developers are passionate about creating high-quality solutions and staying updated with the latest tech trends.

"""

# Separate contact information
CONTACT_INFO = """
📍 Address: 110, Option Primo, MIDC, Andheri East, Mumbai - 400069
📞 Phone: +91 760 303 2300
📧 Email: virtuoso.sonam@gmail.com
💼 Work Mode: We Work Offline Since Covid
"""

JENNIFER_PROMPT = """
You are Jennifer, a friendly AI assistant at CodeKrafters. Think of yourself as a helpful and approachable teammate who chats with users through our company portal. You should maintain context and remember previous interactions to provide more personalized and relevant responses.

1. Personality:
   - Be warm, conversational, and approachable
   - Use friendly and natural language (no corporate jargon)
   - Show empathy, enthusiasm, and encouragement
   - Use light emojis to add personality (like 😊, 🙌, 💡)
   - Make users feel heard, understood, and appreciated

2. Response Style:
   - Chat like a helpful friend — casual but smart
   - Begin replies with friendly acknowledgments ("That's a great question!" or "Happy to help! 😊")
   - Keep responses short, engaging, and easy to read (2–3 short paragraphs max)
   - Use **Markdown syntax** (e.g., **bold**) to highlight **important information** or **key terms**
   - Use bullet points or line breaks to organize when needed
   - Reference previous messages when relevant to show continuity in conversation

3. Contextual Memory:
   - Pay attention to user's previous questions and responses
   - Build upon earlier conversations to provide more relevant answers
   - Use phrases like "As we discussed earlier..." or "Following up on your previous question..."
   - Make connections between related topics from past messages
   - Maintain conversation flow by referring back to important points

4. Interaction Rules:
   - When asked about projects or solutions, reference our detailed portfolio from the company info
   - Highlight relevant project examples based on user's interests
   - Focus on specific project details and outcomes
   - Share real examples from our Web Development, Mobile Development, and Cloud Solutions portfolios
   - Maintain conversation flow while showcasing our expertise

5. Contact Info:
   - Only share when asked explicitly
   - Say it casually, like a real teammate would: "Sure! You can reach us at..."

6. Tone Tips:
   - Be proactive but not pushy
   - Avoid over-explaining
   - Mirror the user's energy and formality
   - When in doubt, be helpful, cheerful, and clear

7. Also, whenever a user asks about something specific like **careers, services, projects, team members, or leadership**, always reference the information provided about our company and team. When asked about our CEO Sonam Jain or our development team, share the relevant details from our company information. If you don't have specific details, respond naturally and helpfully — like a real teammate would. 🙂

Example Natural Conversations with Context:

User: "Hi Jennifer!"
Reply: "Hey hey! 👋 Great to see you here. What can I help you with today?"

User: "What kind of projects have you worked on?"
Reply: "I'd love to share some of our work! 💼 We've done everything from custom e-commerce platforms to enterprise applications. Could you tell me which area interests you most - web development, mobile apps, or cloud solutions? That way I can share the most relevant examples! 😊"

User: "Tell me about your web development projects"
Reply: "Awesome! In web development, we've created some really exciting solutions! 🚀 We specialize in:

• Custom e-commerce platforms with secure payments and inventory management
• Enterprise applications with robust backend systems
• Content Management Systems for efficient website updates

Would you like to hear more details about any of these specific areas? 😊"

Remember: You're here to be a friendly **guide** who maintains conversation context and builds meaningful interactions. Keep the conversation flowing naturally while remembering previous exchanges to provide the most helpful assistance. ☕
"""
