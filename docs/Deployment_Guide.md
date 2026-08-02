# Deployment Guide

## Purpose

OpenPreEduLab uses GitHub for source code, documentation, review history, and
research assets. The interactive Streamlit interface is deployed separately.
This separation keeps the research record inspectable while providing a
browser-based platform experience.

## Recommended deployment: Streamlit Community Cloud

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with
   the GitHub account that has access to `AvelineChuk/OpenPreEduLab`.
2. Select **Create app** and choose the `OpenPreEduLab` repository.
3. Choose the `main` branch.
4. Set the application entry point to:

   ```text
   app/streamlit_app.py
   ```

5. Confirm that the repository `requirements.txt` is used for dependency
   installation.
6. Deploy the app and retain the generated public or access-controlled URL.
7. Add the confirmed URL to the repository README as the **Launch Platform**
   link.

## Private repository note

The current repository may remain private. Streamlit Community Cloud must be
authorised to access it through the repository owner's GitHub account. Do not
publish raw source files, reviewer identifiers, or unapproved datasets merely
to make the application public.

## Deployment boundary

The deployed interface is a research prototype. It defaults to synthetic sample
data and does not turn uploaded files into approved research evidence. Real
data must remain subject to the repository workflow:

`raw → staging → independent review → processed`

## Verification checklist

After deployment, verify that:

- the Landing Page opens before the Dashboard;
- **Launch Platform** enters the Research Platform;
- the sample-data PRAI and Equity pages load;
- the Data page displays the governance notice;
- no raw, staging, or processed private files are exposed through the UI; and
- the deployed URL is recorded accurately in the README.
