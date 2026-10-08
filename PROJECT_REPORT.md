# Final Project Report: Campus Events Discovery App

## 1. Project Overview
The **Campus Events Discovery App** is a full-stack web application designed to bridge the gap between event organizers and students within a college campus. It provides a centralized hub for discovering workshops, fests, and sports events while automating the registration and management process.

## 2. Key Modules Implemented

### User Authentication & Management
- Secure registration and login using Django's Auth system.
- Role-Based Access Control (RBAC): Differentiated permissions for **Students**, **Organizers**, and **Administrators**.
- Detailed Student Profiles featuring ID, Department, and academic year.

### Event Life Cycle
- **Submission**: Organizers submit events with images and deadlines.
- **Approval**: Admins review and approve submissions before they go live.
- **Discovery**: Students browse events via a responsive gallery with categories and live search.
- **Participation**: Integrated RSVP system with digital QR-code tickets.

### Admin & Organizer Dashboards
- **Real-time Analytics**: Visualized data on registrations and popular event trends.
- **Communication**: Automated email broadcasts from organizers to their attendees.
- **Exports**: Ability for organizers to download attendee lists in CSV format for offline use.

## 3. Technology Stack
- **Backend**: Python 3.x, Django 5.x
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6)
- **Styling**: Modern premium design with CSS Variables and Glassmorphism.
- **APIs/Libraries**: Leaflet.js (Maps), FullCalendar (Interactive Calendar), QRServer API.

## 4. Design Aesthetics
The application follows a **Premium Dark Theme** aesthetic:
- **Vibrant Gradients**: Used for primary buttons and accents.
- **Glassmorphism**: Applied to cards and navigation elements for a modern feel.
- **Responsiveness**: Fully optimized for Desktop, Tablet, and Mobile devices.

## 5. Bonus Features Included
- **QR Code Entry**: Automated ticket generation for event check-in.
- **Interactive Map**: Live venue locations for all events.
- **Dark/Light Mode**: User-selectable themes.
- **Countdown Timers**: Visual urgency for upcoming registration deadlines.
- **AI Recommendation Engine**: Smart event suggestions based on user interests.

## 6. Conclusion
The Campus Events Discovery App successfully delivers a robust, secure, and visually stunning solution that meets all academic project requirements. It streamlines campus engagement and provides administrators with the tools necessary to foster a vibrant college community.

---
**Development Team**: Antigravity AI
**Final Submission**: June 2026
