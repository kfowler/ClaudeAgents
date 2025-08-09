# OrbStack Development Environment Manager

Manage your OrbStack containers and development database:

**Container Operations:**
- List running containers and their status
- Start/stop PostgreSQL container with proper port mapping
- Check container logs and resource usage
- Clean up unused containers and images

**Database Management:**
- Connect to PostgreSQL instance running in OrbStack
- Run database migrations and seed data
- Create database backups before major changes
- Monitor database performance and connections

**Environment Sync:**
- Ensure development environment matches production
- Update container images and dependencies
- Verify network connectivity between containers
- Test database connections from application containers

**Troubleshooting:**
- Debug container networking issues
- Resolve port conflicts and binding problems
- Check OrbStack VM resource allocation
- Investigate container startup failures

**Development Workflow:**
- Set up isolated development environments per project
- Handle file system mounting and permissions
- Configure environment-specific variables and secrets
- Test applications in Linux containers before deployment

Operation: $ARGUMENTS

