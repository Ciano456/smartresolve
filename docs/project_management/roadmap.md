# Roadmap

## Current Status

- Phases 0-8 are complete for the agreed MVP, including CSV export.
- Phase 9 security hardening is complete; its deployment, backup, GDPR, and optional
  security-dashboard items remain open.
- Phase 10 code/configuration and runbooks are prepared; live Railway deployment and
  evidence remain tracked by issue #25.
- UAT and final evidence are tracked by issue #26.
- Phase 11 remains future enhancement work.

## Phase 0 - Foundation

1. Clean repo structure
2. Finalise app boundaries
3. Set custom user model
4. Configure settings properly
5. Set up static/media config
6. Set up root URLs
7. Create GitHub repo workflow
8. Add branch strategy
9. Add GitHub Actions CI
10. Add branch protection on main

## Phase 1 - Identity And Access

11. Custom user model
12. Custom user manager
13. Login
14. Logout
15. Create Django groups: Submitter, Support Staff, Admin
16. Permission helpers/decorators/mixins
17. Basic profile/account page
18. Admin portal user list
19. Admin portal create user
20. Admin portal edit user
21. Admin portal activate/deactivate user
22. Admin portal assign group/role

## Phase 2 - Ticket Master Data

23. TicketType lookup model
24. TicketSystem lookup model
25. TicketPriority lookup model
26. TicketStatus lookup model
27. Admin registration for lookup models
28. Admin portal pages to manage lookup values
29. Seed initial lookup values

## Phase 3 - Core Ticket Engine

30. Ticket model
31. Ticket number generation
32. TicketComment model
33. TicketAttachment model
34. TicketHistory model
35. Django admin registration for ticket models
36. Signals or service layer for ticket history creation

## Phase 4 - User Ticket Flow

37. Ticket create form
38. Ticket submit page
39. My tickets list
40. Ticket detail page
41. Add comment to ticket
42. Show visible vs internal comments correctly
43. Upload attachments
44. Download/view attachments
45. Edit ticket rules for submitter where appropriate

## Phase 5 - Staff Workflow

46. Staff ticket queue
47. Assign ticket to user
48. Change status
49. Change priority
50. Add internal notes
51. Add resolution notes
52. Resolve ticket
53. Close ticket
54. Cancel ticket
55. Show ticket history on detail page
56. Filter tickets by status, priority, type, system, requester, assigned user, and date range

## Phase 6 - Admin Portal Configuration

57. Admin dashboard landing page
58. Manage users from UI
59. Manage lookup values from UI
60. View all tickets
61. Bulk admin actions later if needed
62. Optional department/team management later

## Phase 7 - Notifications

63. Email on ticket creation
64. Email on assignment
65. Email on status change
66. Email on comment added
67. Email on resolution/closure
68. Central notification helper/service
69. Email templates

## Phase 8 - Dashboard And Reporting

70. Open tickets count
71. Tickets by status
72. Tickets by priority
73. Tickets by type
74. Tickets by system
75. Assigned workload by staff member
76. Recent activity
77. Closed/resolved trend
78. Average resolution time later
79. Export filters/report data later if needed

## Phase 9 - Audit And Security Hardening

80. Audit trail visibility
81. Failed login logging
82. Access denial logging
83. Security events table if needed
84. Security dashboard summary
85. File upload validation
86. Strong permission checks across views
87. Production settings split
88. Environment variable cleanup
89. Backup/restore plan

## Phase 10 - Deployment

90. Internal staging/UAT setup
91. Production config
92. Static files deployment
93. Media storage path
94. Gunicorn/Uvicorn or chosen app server setup
95. Reverse proxy config if used
96. Collectstatic process
97. Logging configuration
98. Error email/reporting
99. Manual deployment checklist
100. Release checklist

## Phase 11 - Future Enhancement

101. AI ticket categorisation
102. Suggested priority
103. Suggested assignment
104. Knowledge base
105. SLA timers
106. Teams integration
