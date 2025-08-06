# Task 2: Analyze a Phishing Email Sample

## Objective

Examine a suspicious `.eml` file using an EML analyzer to identify phishing characteristics and create a clear, detailed report of findings.

## Tools Needed

- **EML Analyzer**: Online tools like MXToolbox (https://mxtoolbox.com/EmailHeaders.aspx) or Group-IB EML Analyzer, or local tools like Thunderbird.
- **Text Editor**: Notepad or Visual Studio Code to view the raw `.eml` file (optional).
- **Web Browser**: To access online analyzers and check domains/URLs.
- **Antivirus Software**: To scan attachments/links (e.g., Windows Defender).
- **Domain Lookup**: WHOIS or DomainTools to verify sender domains.

## Steps to Analyze the Email

1. **Open the .eml File Safely**

   ![Examples:](screenshot/1.png)

   - Upload the `.eml` file to an online EML analyzer or open it in a local email client (e.g., Thunderbird) or text editor.
   - Do not click links or open attachments to avoid malware.

3. **Check Email Headers**

   - Use the EML analyzer to parse headers (e.g., `From`, `Return-Path`, `Received`).
   - Look for:

     ![Examples:](screenshot/2.png)
     
     - **Spoofed Sender**: Mismatched `From` and `Return-Path` or fake domains (e.g., ).
     - **Suspicious Servers**: Untrusted mail servers in `Received` fields.
     - **Authentication Issues**: Failed SPF, DKIM, or DMARC results.

4. **Review Email Content**

   - Check the email body for phishing signs:
     - **Sender Email**: Does it match the claimed sender’s domain?
     - **Urgent Tone**: Phrases like "Act now!" or "Account locked!"
     - **Generic Greeting**: "Dear User" instead of your name.
     - **Bad Spelling/Grammar**: Typos or unprofessional writing.
     - **Suspicious Links**: Hover (don’t click) to verify URLs match legitimate domains.
     - **Attachments**: Unsolicited files like `.zip` or `.exe`.
     - **Sensitive Info Requests**: Asks for passwords or financial details.

5. **Verify Links and Attachments**

   - **Links**: Use the analyzer’s URL check or tools like VirusTotal to scan URLs without clicking.
   - **Attachments**: Scan with antivirus before opening; avoid executables (e.g., `.exe`).
   - **Domains**: Check linked domains with WHOIS for recent or suspicious registrations.

6. **Spot Social Engineering**

   - Look for tactics like:
     - **Impersonation**: Posing as a bank, coworker, or authority.
     - **Urgency**: Pressuring quick action (e.g., "Account expires soon!").
     - **Temptation**: Fake rewards or offers to lure clicks.
     - **Authority**: Mimicking CEOs or officials to intimidate.

7. **Write the Report**

   - Summarize findings in a clear report:
     - Header issues (e.g., spoofed sender, failed DKIM).
     - Content red flags (e.g., urgent tone, fake URLs).
     - Social engineering tactics.
     - Recommendations (e.g., report, delete).
   - Save as a Markdown, Word, or PDF file.

## Deliverable

- **Phishing Analysis Report**: A simple, detailed document listing:
  - Email details (subject, sender, date).
  - Header issues (e.g., spoofing, failed authentication).
  - Content red flags (e.g., suspicious links, urgent language).
  - Social engineering tactics.
  - Actions to take (e.g., report to IT, delete email).

## Safety Tips

- Don’t click links or open attachments unless scanned and safe.
- Use a virtual machine or sandbox for analysis if possible.
- Report suspicious emails to your IT team or anti-phishing groups (e.g., report@apwg.org)..
