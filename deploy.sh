#!/bin/bash
# Production deployment script

set -e

echo "🚀 TriLLM Arena - Production Deployment"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Docker
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker Compose
echo -e "${YELLOW}Checking Docker Compose installation...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Create .env if not exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created (please customize if needed)${NC}"
fi

# Replace old files with new ones
echo -e "${YELLOW}Updating Python files...${NC}"
if [ -f trillm_arena/llm_updated.py ]; then
    mv trillm_arena/llm_updated.py trillm_arena/llm.py
    echo -e "${GREEN}✓ Updated llm.py${NC}"
fi

if [ -f trillm_arena/debate_engine_updated.py ]; then
    mv trillm_arena/debate_engine_updated.py trillm_arena/debate_engine.py
    echo -e "${GREEN}✓ Updated debate_engine.py${NC}"
fi

if [ -f trillm_arena/app_updated.py ]; then
    cp trillm_arena/app_updated.py trillm_arena/app.py
    echo -e "${GREEN}✓ Updated app.py${NC}"
fi

if [ -f trillm_arena/api_updated.py ]; then
    mv trillm_arena/api_updated.py trillm_arena/api.py
    echo -e "${GREEN}✓ Updated api.py${NC}"
fi

# Start services
echo -e "${YELLOW}Starting Docker services...${NC}"
docker-compose up -d

# Wait for services
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check health
echo -e "${YELLOW}Checking service health...${NC}"
if docker-compose ps | grep -q "healthy"; then
    echo -e "${GREEN}✓ All services healthy${NC}"
else
    echo -e "${YELLOW}⚠ Services still starting, please wait...${NC}"
    docker-compose ps
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Access your application at:"
echo -e "${YELLOW}  Web UI:   http://localhost:8501${NC}"
echo -e "${YELLOW}  API:      http://localhost:8000${NC}"
echo -e "${YELLOW}  API Docs: http://localhost:8000/api/docs${NC}"
echo ""
echo "View logs:"
echo -e "${YELLOW}  docker-compose logs -f${NC}"
echo ""
