
This is a personal growth project to improve my software engineering skill and not meant to be / become a professional software product. 
Start: 09.10.2025
End: 31.12.2025 (first live version, no UI)
Learning Goals:
- Build a DDD-based application to understand DDD
- Build a proper Identity and Access Management solution as supporting subdomain
- Gain UI/Frontend experience
- Gain experience in making engineering trade-offs
- Understand underlying software design principles (e.g. SOLID) by application
- Gain experience in Github-based CI/CD
- Gain experience in operations

If you are interested in following this project, follow my blog here: 

# Caucus Expense Tracker

## Value Proposition
Allows to track expenses right for Fraktion (Caucus) in any Stadtrat (municipal parlament) in Germany. Along with classic cost tracking, the CET combines easy to add receipt adding and rules based expense tracking with on-demand report generation for every Rechenschaftsbericht (Transparency Report) and official expense report.

### Main Features
- Expense tracking
- Expense overviews and visualizations
- Receipt upload and attachment to expense
- Customizable expense categories
- Stable official categories
- Expense report generation
- Transparency report generation
- Balance overview and status

### Other features
- User-based login via PW with MFA
- Role-based access for Admin, normal users and other roles
- Email-based backup (interim)
- Customizable accounting periods
- Customizable notification for users 
- Invite-link based user registration based on One-time-token and addressed email
- Email verification flow
- User Settings
	- Change email
	- Change password

## Technical Setup
- Basic containerized application 
- Backend Fastapi
- Frontend React
- Running on VPS with small footprint
- Backups are stored somewhere securely

## Implementation Plan
- Start with strategic design of the application in the different domains
- Define core domain, supporting domains and generic subdomains
- Define bounded context and components within
- Define Interfaces between different contexts
- Implement core domain
