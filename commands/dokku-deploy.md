# Dokku Deployment on Pi

Handle deployment to your pi server via dokku:

**Pre-deployment:**
- Check current deployment status on pi
- Verify git repository is clean and ready
- Run local tests and build verification
- Check dokku app health and resources on pi

**Deployment Process:**
- Push to dokku git remote on pi
- Monitor deployment logs in real-time
- Verify application startup and health checks
- Test critical endpoints post-deployment

**Configuration Management:**
- Manage environment variables via dokku config
- Handle SSL certificates and domain configuration
- Monitor nginx proxy configuration
- Manage database connections and migrations

**Rollback & Recovery:**
- Implement rollback to previous version if needed
- Debug deployment failures and error logs
- Check dokku processes and restart if necessary
- Verify disk space and resource availability on pi

**SSH Operations:**
- Connect to pi and run dokku commands
- Check system resources and docker containers
- Monitor application logs and performance
- Manage dokku plugins and updates

**Service Management:**
- Scale applications up/down based on load
- Manage linked services (databases, redis, etc.)
- Handle zero-downtime deployments
- Configure health checks and monitoring

App/Action: $ARGUMENTS

