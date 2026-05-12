# TodayBank GRC Demo – Marketing Team Talk Track (4 min)

A focused persona demo for marketing analysts and digital/product marketers. Run this standalone or as a bookend after Act 5 of the main 30-min demo.

**Audience:** Marketing analysts, campaign managers, digital marketers, product managers
**Hook:** You have behavioral data about every customer – let's actually use it

---

## Pre-flight

Open two tabs before you start:
1. Genie space "TodayBank GRC Operations Hub"
2. `todaybank_grc_demo.silver.complaints_classified` in Catalog Explorer (for the data peek)

---

## Talk track

### 0:00 – Frame the opportunity (30 sec)

No screen yet. Face the room.

> "Everything I just showed the Risk team – the 100,000 transactions, the 5,000 customer records, the complaint themes – that's the same data your marketing team is trying to get a hold of to understand customer behavior. The difference is that today, getting a custom segment or answering a product question means filing a ticket and waiting two weeks.
>
> Let me show you what it looks like when marketing can just ask."

---

### 0:30 – Genie: customer segmentation, natural language (1 min 30 sec)

Open the Genie space.

> "This is Genie. It's connected to the same governed views your Risk team uses – same access controls, same data. I'm going to ask it a question a campaign manager might actually have."

Type:
> *"Show me customers aged 25 to 45 who have a mortgage and have not had any complaints in the last 12 months, ranked by account balance."*

Wait for the response. Click "Show SQL".

> "Notice a few things. It returned a real answer – a ranked list of your happiest, highest-balance mid-career customers. These are your cross-sell targets. And it shows the SQL it ran – your team can verify it, copy it into a notebook, or schedule it as a weekly export to your CRM. There's no black box."

Type a follow-up:
> *"How many of those customers are in California and Arizona combined?"*

Wait.

> "Same session context. It remembered the filter. An analyst can iterate through a whole segmentation exercise without writing a line of SQL – and every query they run is audited. If someone accidentally queries beyond their permission level, Unity Catalog blocks it and logs it."

---

### 2:00 – Complaint themes as a product signal (1 min)

Switch to Catalog Explorer → `silver.complaints_classified`. Click Sample Data.

> "Here's where it gets interesting for product and marketing. We classified 500 customer complaints using a single SQL function – `ai_classify`. Look at the theme column: `fees`, `loan_servicing`, `account_access`, `credit_reporting`.
>
> This is a real-time voice-of-the-customer signal. If you're planning a campaign around a new fee structure and complaints in the `fees` bucket are trending up week over week, you know before launch. If `account_access` spikes after a mobile app release, your digital team sees it here.
>
> The severity column tells you how loud the customer was. A high-severity `loan_servicing` complaint from a customer with a $400k mortgage is a very different retention risk than a low-severity `fees` complaint from a checking account customer."

---

### 3:00 – Close + what this unlocks (1 min)

> "The pattern here is the same as what the Risk team got: one data layer, one governed access model, one place to ask questions.
>
> For marketing, specifically, what this unlocks is:
>
> First – **customer intelligence without waiting for a data pull.** Genie answers the segmentation and cohort questions your team asks ten times a week, right now, on live data.
>
> Second – **complaint trends as a campaign signal.** You see what's frustrating customers in the same platform where you build the segments. You don't need a separate survey tool.
>
> Third – **safe self-service.** Analysts can explore freely. Unity Catalog enforces what they can and can't see – PII masking, row-level filters by region or product line. Marketing gets access without IT having to build a separate masked copy of the data.
>
> The same demo environment your Risk Officer uses on Monday morning is the one your campaign manager can use on Thursday afternoon."

---

## Q&A hooks

| Common marketing question | Crisp answer |
|---|---|
| "Can we connect this to Salesforce or our CRM?" | Yes – Databricks has native connectors to Salesforce, HubSpot, and most major CRMs. The segment query in Genie becomes a scheduled job that pushes a list to your CRM daily. |
| "What about A/B test results – can we analyze those here?" | Yes – if your experimentation platform logs to S3/ADLS/GCS, Lakeflow ingests it and it lands in the same governed catalog. Genie can answer A/B questions in natural language. |
| "We use Tableau / Looker today – do we have to switch?" | No – AI/BI Dashboards are Databricks-native and are great for new dashboards, but you can also keep Tableau pointed at Databricks SQL. Same governed views, same lineage. |
| "How fresh is the data?" | Depends on pipeline schedule – the demo runs batch. For campaign analytics, daily refresh is typical. For real-time customer signals, Lakeflow runs streaming continuously. |
| "Can we let our agency access specific segments?" | Yes – Unity Catalog row filters and column masks can give an external agency access to a specific subset of customers without exposing PII or cross-segment data. |
