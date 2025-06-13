# 📝 Urban Mobility Compliance Report

## BACKUP & RESTORE
- ❌ Backup includes DB file zipped *(Not implemented)*
- ❌ Super Admin can restore any backup *(Not implemented)*
- ❌ System Admin can restore with one-time code *(Not implemented)*
- ❌ Data must be encrypted before backup *(Not implemented)*

## DATABASE & ENCRYPTION
- 🟡 Encrypt usernames, phone numbers, addresses, and logs *(Partial: encryption utilities and methods present, but not fully integrated everywhere)*
- 🟡 Store only cryptographic hashes of passwords using salt *(Partial: crypto_utils provided, but not used in all flows)*
- ❌ Never decrypt data for storage; always encrypted at rest *(Not implemented)*

## GENERAL SYSTEM REQUIREMENTS
- ✅ Console-based Python 3 application *(Implemented)*
- ✅ Use SQLite3 as local database *(Implemented)*
- 🟡 Encrypt all sensitive data (symmetric encryption) *(Partial: utilities present, not fully integrated)*
- 🟡 Store only hashed passwords, never plaintext *(Partial: crypto_utils provided, not used everywhere)*
- ✅ Use standard libraries + sqlite3, re, and any crypto/hash library *(Implemented)*
- ✅ Main file must be named um_members.py *(Implemented)*
- ❌ Submission should be a .zip with source code and PDF of group members *(Not applicable in code)*

## LOGGING SYSTEM
- 🟡 Log all activities with time, username, activity, and suspicious flag *(Partial: logs time, username, action, but no suspicious flag)*
- ❌ Detect and flag suspicious activities (e.g. multiple failed logins) *(Not implemented)*
- ❌ Only view logs through system interface (Super/System Admin only) *(Not implemented)*

## SCOOTER DATA
- 🟡 Add/edit/delete scooters (Super/System Admin only) *(Partial: code structure present, but not fully implemented)*
- ✅ Each scooter includes brand, model, serial number (10–17 alphanum), top speed, etc. *(Implemented in schema)*
- ❌ Service Engineers can only edit specific fields *(Not implemented)*

## SECURITY PRACTICES FROM LESSONS
- 🟡 Validate both user- and server-generated input *(Partial: some validation present)*
- ❌ Reject and log invalid input (don’t modify it) *(Not implemented)*
- ❌ Use HTML encoding if applicable to browser outputs *(Not applicable: console app)*
- 🟡 Store hashed passwords using salt *(Partial: crypto_utils provided, not used everywhere)*
- ❌ Use secure encryption and monitor log anomalies *(Not implemented)*

## SECURITY REQUIREMENTS
- 🟡 Validate all input using whitelisting principles *(Partial: some input validation)*
- 🟡 Prevent SQL injection (use prepared statements) *(Partial: parameterized queries used in some places)*
- ❌ Encrypt logs and make them unreadable outside the system *(Not implemented)*
- 🟡 Implement role-based access control for all users *(Partial: role checks in menus, but not enforced everywhere)*
- 🟡 Enforce username rules (8-10 chars, starts with letter/_ etc.) *(Implemented in verification)*
- 🟡 Enforce password rules (12-30 chars, at least 1 lowercase, 1 uppercase, 1 digit, 1 special character) *(Implemented in verification)*

## TRAVELLER DATA
- 🟡 Add/edit/delete traveller records (Super/System Admin) *(Partial: schema present, not fully implemented)*
- ✅ Fields include name, birthday, gender, address, zip (DDDDXX), city, email, phone, license number *(Implemented in schema)*
- ❌ Auto-generate registration date and unique ID *(Not implemented)*

## UI & INTERACTION
- 🟡 Clear display of options and input formats *(Partial: some menus clear, but not all)*
- 🟡 Input options should be case-insensitive (e.g. '1', 'R', 'r') *(Partial: not everywhere)*
- ✅ Interface must be usable by teacher during grading *(Implemented: console-based)*

## USER FUNCTIONALITY - Service Engineer
- ❌ Modify allowed scooter attributes *(Not implemented)*
- ❌ Update own password *(Not implemented)*
- ❌ Search scooter information *(Not implemented)*

## USER FUNCTIONALITY - Super Administrator
- 🟡 Full access to all system functions *(Partial: menu structure present)*
- 🟡 Manage System and Service Admins *(Partial: system admin management present)*
- ❌ Generate and revoke restore-codes *(Not implemented)*
- ❌ Cannot change own password *(Not enforced)*

## USER FUNCTIONALITY - System Administrator
- 🟡 Manage Service Engineers and Travellers *(Partial: menu structure present)*
- 🟡 CRUD operations for scooters and travellers *(Partial: code structure present)*
- ❌ Reset Service Engineer passwords *(Not implemented)*
- ❌ Make and restore backups (with code) *(Not implemented)*
- ❌ View logs *(Not implemented)*

---

**Legend:**
- ✅ Fully implemented
- 🟡 Partially implemented
- ❌ Not implemented

**Summary:**
- Many core structures and validation are present, but encryption, backup/restore, logging, and some role-based features are missing or incomplete. See above for details.
