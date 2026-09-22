# Greenhill Food Co-op

A web-based ordering management system developed for **ISYS3001 Managing Software Development**.

This repository is used for both **Assessment 2 (Configuration and Procurement Management)** and **Assessment 3 (SCRUM Project Management)**.

The project aims to provide a simple and reliable system for managing weekly food co-op orders while demonstrating software configuration management, version control, testing, release management, and Scrum-based teamwork.

---

## Project Overview

Greenhill Food Co-op currently manages weekly grocery orders using manual forms and spreadsheets.

This project provides a web application that allows:

* Members to view available products.
* Members to create, update, and cancel weekly orders.
* Coordinators to manage members, products, and weekly ordering rounds.
* Coordinators to review all submitted orders.
* The system to calculate order totals correctly for products sold by unit or by weight.
* Packing volunteers to access packing information.
* Project team members to manage development through GitHub and Jira.

---

## Core Features

### Member

* Secure login
* View products available in the current ordering round
* Place an order
* Edit an order while the round is open
* Cancel an order while the round is open
* View previous orders
* View calculated order totals
* Access only their own order information

### Coordinator

* Manage members
* Add and update products
* Withdraw unavailable products
* Manage weekly ordering rounds
* Open and close ordering rounds
* View all member orders
* View product totals for purchasing
* Access packing information
* Review system activity

### Packer

* View packing sheets
* View crate and product information
* Record actual packed quantities
* Record packing initials
* Record short supply or packing notes

---

## Pricing Rules

The application supports two product pricing methods.

### Products sold by unit

Example:

```text
2 dozen eggs × $7.50 = $15.00
```

### Products sold by weight

Example:

```text
1.58 kg oats × $3.40/kg = $5.37
```

The system keeps the product price associated with the ordering round so that historical orders are not affected by later price changes.

---

## Technology Stack

### Backend

* Python
* FastAPI
* SQLite

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2 Templates

### Development and Configuration

* Git
* GitHub
* GitHub Actions
* Pytest
* Environment configuration
* Docker support

### Project Management

* Jira
* Scrum
* Product Backlog
* Sprint Backlog
* Sprint Planning
* Testing
* Release Management

---

## Repository Structure

```text
greenhill-food-coop/
│
├── app/
│   ├── routers/
│   ├── services/
│   ├── templates/
│   ├── static/
│   ├── main.py
│   ├── db.py
│   ├── config.py
│   └── security.py
│
├── tests/
├── scripts/
├── docs/
├── .github/
│   └── workflows/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── CHANGELOG.md
├── README.md
└── run.py
```

---

## Branching Strategy

The project uses a feature-branch workflow.

### Main Branch

```text
main
```

`main` contains the stable version of the project.

Development work should not normally be performed directly on this branch.

### Zhihe Zhang Development Branch

```text
feature/zhihe-zhang
```

This branch is used for development work completed by **Zhihe Zhang**.

For Assessment 3, additional branches may be created from Jira user stories, for example:

```text
feature/MSD426GXUST34-5-member-login
feature/MSD426GXUST34-6-product-list
feature/MSD426GXUST34-7-place-order
feature/MSD426GXUST34-8-edit-order
```

Completed work should be reviewed through a Pull Request before being merged into `main`.

---

## Git Workflow

Typical development workflow:

```text
Jira Story
    ↓
Create Feature Branch
    ↓
Develop Feature
    ↓
Run Tests
    ↓
Commit Changes
    ↓
Push Branch
    ↓
Create Pull Request
    ↓
Code Review
    ↓
Merge into main
    ↓
Update Jira Story
```

Example commit messages:

```text
Add member authentication
Implement product management
Add weekly ordering workflow
Fix weighted product pricing
Add packing sheet view
Add order validation tests
Update deployment configuration
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zhihe-zhang1/greenhill-food-coop.git
cd greenhill-food-coop
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a local `.env` file using:

```text
.env.example
```

Do not commit passwords, API keys, or other sensitive information to GitHub.

### 5. Start the Application

```bash
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

---

## Demo Accounts

### Coordinator

```text
Email: coordinator@greenhill.local
Password: Coordinator123!
```

### Member

```text
Email: member@greenhill.local
Password: Member123!
```

### Packer

```text
Email: packer@greenhill.local
Password: Packer123!
```

These accounts are demonstration accounts only and do not contain real personal information.

---

## Running Tests

Run the automated tests with:

```bash
pytest -q
```

Tests cover important project behaviour including:

* Authentication
* Order creation
* Order validation
* Unit pricing
* Weight-based pricing
* Product management
* Round management
* Packing functionality
* API permissions

---

## Configuration Management

Configuration management practices used in the project include:

* Git version control
* Feature branches
* Pull Requests
* Meaningful commit messages
* Change logs
* Environment configuration
* Dependency management
* Automated testing
* GitHub Actions
* Deployment configuration
* Version and release management

Environment-specific or sensitive values should not be stored directly in the source code.

---

## Assessment 2

Assessment 2 focuses primarily on:

* Version control
* Branching strategy
* Configuration management
* Application configuration
* Deployment configuration
* Change documentation
* GitHub activity
* Procurement planning
* Request for Proposal (RFP)

The source code and Git history in this repository provide evidence of the configuration-management process.

---

## Assessment 3

Assessment 3 continues development of the same software project.

The team will use Jira and Scrum to manage:

* Product Backlog
* User Stories
* Acceptance Criteria
* Story Points
* Sprint Planning
* Sprint Backlog
* Development Tasks
* Test Plans
* Test Results
* Software Releases
* Sprint Review
* Retrospective
* Project Closure

Jira is used for project-management artefacts, while GitHub is used for source-code and version management.

---

## Team Workflow

Assessment 3 is completed as a team project.

Each team member is expected to:

* Participate in planning
* Take responsibility for assigned Jira issues
* Create development branches
* Commit their own work
* Participate in code review
* Participate in testing
* Contribute to project documentation
* Take turns performing project-management responsibilities

### Team Members

| Name          | Role                            |
| ------------- | ------------------------------- |
| Zhihe Zhang   | Developer / Project Team Member |
| Team Member 2 | Developer / Project Team Member |
| Team Member 3 | Developer / Project Team Member |

Roles may rotate during the project according to the Scrum and project-management plan.

---

## Definition of Done

A feature should only be considered complete when:

* The acceptance criteria are satisfied.
* The implementation is committed to GitHub.
* The work is completed on an appropriate feature branch.
* Automated tests have been added where appropriate.
* Existing tests continue to pass.
* A Pull Request has been reviewed.
* Review comments have been addressed.
* The feature has been merged into the stable branch.
* Relevant Jira information has been updated.
* Necessary documentation has been updated.

---

## Release Management

Stable project versions are released from the `main` branch.

Example release tags:

```text
v0.1.0
v0.2.0
v1.0.0
```

Suggested project milestones:

```text
v0.1.0 - Initial application structure
v0.2.0 - Assessment 2 working version
v0.5.0 - Scrum development version
v1.0.0 - Assessment 3 final release
```

---

## Out of Scope

The initial project does not aim to implement every possible co-op service.

Potential future backlog items may include:

* Online payment processing
* Bank reconciliation
* Accounting-system integration
* Supplier-system integration
* SMS notifications
* Email notifications
* Native mobile applications
* Delivery management

These items may be considered for future iterations.

---

## Security

The project uses basic security practices including:

* Password hashing
* Authentication
* Role-based access control
* CSRF protection
* Environment-based configuration
* Separation of sensitive configuration from source code

No real passwords, student IDs, financial information, or personal credentials should be committed to this repository.

---

## Documentation

Supporting project documentation is maintained under:

```text
docs/
```

Current repository documentation includes:

* [Configuration management](docs/CONFIGURATION_MANAGEMENT.md)
* [Git workflow](docs/GIT_WORKFLOW.md)
* [Deployment instructions](docs/DEPLOYMENT.md)
* [Assessment 2 evidence checklist](docs/A2_EVIDENCE_CHECKLIST.md)
* [Change log](CHANGELOG.md)

Assessment 3 documentation may additionally include Jira mapping, sprint planning, test plans, release plans and project handover material

---

## Author

**Zhihe Zhang**

ISYS3001 Managing Software Development

Greenhill Food Co-op Project
