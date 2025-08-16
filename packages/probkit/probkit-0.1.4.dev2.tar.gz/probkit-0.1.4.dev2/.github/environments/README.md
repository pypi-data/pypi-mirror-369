# GitHub Environment Configuration
# 
# This file documents the 'release' environment configuration.
# You'll need to manually create this environment in your GitHub repository settings.
#
# To create the environment:
# 1. Go to your repo on GitHub
# 2. Settings → Environments → New environment
# 3. Name it: release
# 4. Add protection rules (optional):
#    - Required reviewers (if you want manual approval)
#    - Deployment branches (restrict to main/master only)
#
# The environment name 'release' matches what's specified in publish.yml

Environment Name: release
Purpose: PyPI publishing workflow
Required Permissions: id-token:write (for OIDC trusted publishing)
