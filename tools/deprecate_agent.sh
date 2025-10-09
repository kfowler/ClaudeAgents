#!/bin/bash
#
# Agent Deprecation Helper Script
# Automates the process of deprecating an agent with proper checks and documentation
#
# Usage: ./tools/deprecate_agent.sh <agent-name>
#

set -e  # Exit on error

AGENT_NAME=$1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}Warning: $1${NC}"
}

success() {
    echo -e "${GREEN}$1${NC}"
}

info() {
    echo -e "${BLUE}$1${NC}"
}

# Check usage
if [ -z "$AGENT_NAME" ]; then
    echo "Usage: ./tools/deprecate_agent.sh <agent-name>"
    echo ""
    echo "Example: ./tools/deprecate_agent.sh my-old-agent"
    echo ""
    echo "This script will:"
    echo "  1. Verify the agent exists"
    echo "  2. Verify death certificate exists"
    echo "  3. Move agent to agents/deprecated/"
    echo "  4. Guide you through documentation updates"
    exit 1
fi

# Get repository root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$REPO_ROOT"

info "Agent Deprecation Helper"
info "======================="
echo ""

# Check agent exists
AGENT_FILE="agents/$AGENT_NAME.md"
if [ ! -f "$AGENT_FILE" ]; then
    error "Agent file not found: $AGENT_FILE"
fi
success "✓ Agent file found: $AGENT_FILE"

# Check death certificate exists
DEATH_CERT="tools/death_certificates/$AGENT_NAME.md"
if [ ! -f "$DEATH_CERT" ]; then
    error "Death certificate not found: $DEATH_CERT

Before deprecating, you must create a death certificate:
  1. Copy the template: cp tools/death_certificates/TEMPLATE.md $DEATH_CERT
  2. Fill in all required sections
  3. Get peer review from the-critic
  4. Re-run this script

See: docs/contributing.md#agent-deprecation-and-death-certificates"
fi
success "✓ Death certificate found: $DEATH_CERT"

# Extract cause of death from certificate for commit message
CAUSE=$(grep -m 1 "**Cause of Death:**" "$DEATH_CERT" | sed 's/.*\[Category: \(.*\)\].*/\1/' || echo "Unknown")
success "✓ Cause of death: $CAUSE"

# Validate death certificate format
info ""
info "Validating death certificate format..."
if ! grep -q "## Detailed Autopsy" "$DEATH_CERT"; then
    warning "Death certificate may be incomplete (missing 'Detailed Autopsy' section)"
fi
if ! grep -q "## Lessons Learned" "$DEATH_CERT"; then
    warning "Death certificate may be incomplete (missing 'Lessons Learned' section)"
fi
if ! grep -q "## Migration Path" "$DEATH_CERT"; then
    warning "Death certificate may be incomplete (missing 'Migration Path' section)"
fi

# Show summary
echo ""
info "Summary:"
echo "  Agent: $AGENT_NAME"
echo "  Cause: $CAUSE"
echo "  Certificate: $DEATH_CERT"
echo ""

# Confirm deprecation
echo "This will:"
echo "  1. Create agents/deprecated/ directory (if needed)"
echo "  2. Move $AGENT_FILE to agents/deprecated/$AGENT_NAME.md"
echo ""

read -p "Proceed with deprecation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    info "Deprecation cancelled."
    exit 0
fi

# Execute deprecation
info ""
info "Executing deprecation..."

# Create deprecated directory if it doesn't exist
mkdir -p agents/deprecated
success "✓ Created/verified agents/deprecated/ directory"

# Move agent file
git mv "$AGENT_FILE" "agents/deprecated/$AGENT_NAME.md"
success "✓ Moved agent to agents/deprecated/$AGENT_NAME.md"

# Run validation to check for issues
info ""
info "Running validation checks..."
if python3 tools/validate_agents.py 2>&1 | grep -q "Error"; then
    warning "Validation found some issues. Review output above."
else
    success "✓ Validation passed"
fi

# Generate next steps
echo ""
success "Agent deprecated successfully!"
echo ""
info "Next steps (manual):"
echo ""
echo "1. Update CLAUDE.md:"
echo "   - Remove '$AGENT_NAME' from agent selection guide"
echo "   - Remove any keyword mappings to this agent"
echo ""
echo "2. Update death certificates gallery:"
echo "   Run: python3 tools/death_certificates/analyze_certificates.py"
echo "   Then update tools/death_certificates/README.md with new statistics"
echo ""
echo "3. Check for command references:"
echo "   grep -r \"$AGENT_NAME\" commands/"
echo "   Update any commands that referenced this agent"
echo ""
echo "4. Commit changes:"
cat << EOF
   git add .
   git commit -m "Deprecate $AGENT_NAME (see death certificate)

Agent has been deprecated due to: $CAUSE
See tools/death_certificates/$AGENT_NAME.md for full analysis.

Migration path documented in death certificate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
EOF
echo ""
echo "5. Update CHANGELOG.md with deprecation notice"
echo ""

info "Deprecation helper complete!"
