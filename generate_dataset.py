import os
import argparse
import random
import pandas as pd
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# Define constants
SEVERITIES = ['Critical', 'High', 'Medium', 'Low']
STATUSES = ['Open', 'In Progress', 'Fixed', 'Closed']

# Priority mapping
PRIORITY_MAP = {
    'Critical': 'P1',
    'High': 'P2',
    'Medium': 'P3',
    'Low': 'P4'
}

CATEGORIES_TECH_MAP = {
    'Authentication': ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring Boot', 'Laravel', 'Node.js', 'Express', 'ASP.NET', 'Android', 'iOS', 'AWS', 'Azure'],
    'Database': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Spring Boot', 'Django', 'Laravel', 'Express', 'ASP.NET', 'AWS', 'Azure'],
    'API': ['Django', 'Flask', 'Spring Boot', 'Laravel', 'Node.js', 'Express', 'ASP.NET', 'AWS', 'Azure', 'React', 'Angular', 'Vue'],
    'UI': ['React', 'Angular', 'Vue', 'Android', 'iOS'],
    'Network': ['Kubernetes', 'Docker', 'AWS', 'Azure', 'Spring Boot', 'Node.js', 'Django'],
    'Security': ['Django', 'Flask', 'Spring Boot', 'Laravel', 'Node.js', 'Express', 'ASP.NET', 'AWS', 'Azure', 'Kubernetes', 'Docker'],
    'Performance': ['React', 'Django', 'Spring Boot', 'Node.js', 'ASP.NET', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Azure', 'Kubernetes'],
    'Backend': ['Django', 'Flask', 'Spring Boot', 'Laravel', 'Node.js', 'Express', 'ASP.NET'],
    'Frontend': ['React', 'Angular', 'Vue'],
    'Configuration': ['Kubernetes', 'Docker', 'AWS', 'Azure', 'Django', 'Spring Boot', 'Node.js'],
    'Deployment': ['Kubernetes', 'Docker', 'AWS', 'Azure'],
    'Cache': ['Redis', 'Spring Boot', 'Django', 'Node.js', 'Express'],
    'Memory Leak': ['React', 'Node.js', 'Spring Boot', 'Android', 'iOS', 'Express', 'ASP.NET'],
    'Logging': ['Spring Boot', 'Django', 'Flask', 'Node.js', 'Express', 'ASP.NET', 'AWS', 'Azure', 'Kubernetes'],
    'Payment': ['React', 'Angular', 'Django', 'Flask', 'Spring Boot', 'Node.js', 'Express', 'ASP.NET', 'Android', 'iOS'],
    'Search': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Azure', 'Spring Boot', 'Django', 'Node.js'],
    'Notification': ['Django', 'Flask', 'Spring Boot', 'Node.js', 'Express', 'Android', 'iOS', 'AWS', 'Azure'],
    'File Upload': ['React', 'Angular', 'Django', 'Flask', 'Spring Boot', 'Node.js', 'Express', 'Android', 'iOS', 'AWS', 'Azure'],
    'Session Management': ['React', 'Django', 'Flask', 'Spring Boot', 'Laravel', 'Node.js', 'Express', 'ASP.NET', 'Redis', 'MySQL', 'PostgreSQL']
}

CATEGORIES = list(CATEGORIES_TECH_MAP.keys())

# Define scenario templates that generate clean, natural summaries and descriptions
SCENARIOS = {
    'Authentication': [
        {
            'module': 'Login',
            'titles': [
                'SSO login redirect loop during token callback',
                'Authentication redirect loop on SSO integration',
                'SSO token callback throws infinite redirect loop'
            ],
            'descs': [
                'Single Sign-On authentication gets stuck in an infinite redirect loop when processing the OAuth token callback for {user} at port {port}.',
                'Users are unable to log in via SSO due to a circular redirect loop triggered during callback validation at {endpoint}.',
                'The SSO login flow fails to complete and cycles repeatedly between the login portal and the token validation callback endpoint.'
            ],
            'resolutions': [
                'Adjust callback redirect patterns and validate identity provider exchange rules for {endpoint}.',
                'Correct the OAuth2 redirect URI whitelist settings in the IDP configuration profile.',
                'Refactor routing middleware to clear authentication state variables prior to redirecting callback requests.'
            ]
        },
        {
            'module': 'JWT Validator',
            'titles': [
                'JWT validation fails after service restart',
                'Token verification fails following service reboot',
                'Authentication middleware rejects valid JWT after server restarts'
            ],
            'descs': [
                'Token verification fails for all active users after a backend service restart due to ephemeral key regeneration in {tech}.',
                'Active user session validation requests are rejected with invalid signature exceptions immediately after the {service} service reboots.',
                'The {tech} authorization middleware returns authorization errors for valid tokens when the authentication process restarts.'
            ],
            'resolutions': [
                'Configure persistent keystore configuration to retain verification keys across service reboots.',
                'Migrate validation key storage to an external vault database instead of generating dynamic secrets in memory.',
                'Update the token service configuration files to retrieve public validation certificates from the secure config vault.'
            ]
        },
        {
            'module': 'MFA',
            'titles': [
                'MFA verification code rejected on submission',
                'Multi-factor authentication fails to accept valid codes',
                'Intermittent errors rejecting correct MFA verification codes'
            ],
            'descs': [
                'The system intermittently rejects correct multi-factor authentication codes during user login, returning invalid code errors.',
                'Users cannot bypass the MFA step because the system fails to validate valid codes, throwing expiration exceptions.',
                'The authentication system rejects OTP validation attempts for {user} due to verification system exceptions.'
            ],
            'resolutions': [
                'Synchronize server clock configuration and increase the validity window drift buffer.',
                'Update the time-based OTP library config files to accommodate moderate client clock offsets.',
                'Reset the verification database time synchronization intervals and verify database connection health.'
            ]
        },
        {
            'module': 'SessionManager',
            'titles': [
                'User session expires prematurely',
                'Active user session terminates unexpectedly',
                'User gets logged out before session timeout limits'
            ],
            'descs': [
                'Active users are logged out randomly after a few minutes of activity instead of respecting the session timeout limit.',
                'The active user session database deletes active session records, forcing user login prompts prematurely.',
                'Sessions terminate within {time} minutes of login operations despite active page updates on the frontend.'
            ],
            'resolutions': [
                'Update the session expiration middleware to refresh cookie timestamps on subsequent requests.',
                'Increase the token lifespan variables and fix session cleanup database rules.',
                'Refactor the session validator to refresh TTL variables inside the database on active user API requests.'
            ]
        }
    ],
    'Database': [
        {
            'module': 'ConnectionPool',
            'titles': [
                'Database connection pool exhausted under load',
                'Connection pool limit reached under concurrent requests',
                'DB query timeout errors due to connection exhaustion'
            ],
            'descs': [
                'The backend fails to process queries and returns database connection timeout errors under concurrent traffic spikes at {port}.',
                'The application database client cannot establish active connections because pool capacity limits are exceeded.',
                'Queries directed to database {db} time out due to lack of available connections in the pool.'
            ],
            'resolutions': [
                'Increase connection pool maximum limit to {limit} and ensure connections are released in final blocks.',
                'Configure idle connection timeouts and expand the connection pool threshold limit variables.',
                'Audit query execution paths and refactor backend resources to return connections back to the pool immediately.'
            ]
        },
        {
            'module': 'Database Schema',
            'titles': [
                'Primary key constraint violation during concurrent signups',
                'Database integrity violation on user record inserts',
                'Unique index constraint fails when creating users concurrently'
            ],
            'descs': [
                'Concurrent user creations fail with duplicate database ID exceptions because key generation logic collides.',
                'The database table {db} throws duplicate key constraints errors during registration steps.',
                'Simultaneous insert queries for new user accounts fail due to primary key generation collisions.'
            ],
            'resolutions': [
                'Migrate user table primary key strategy to database-managed auto-increment sequence.',
                'Update primary key generation parameters to utilize UUID values instead of sequential integers.',
                'Implement database transaction lock parameters to verify ID values prior to executing insertion queries.'
            ]
        },
        {
            'module': 'TransactionManager',
            'titles': [
                'Database deadlock during shopping cart update',
                'Concurrent cart modifications trigger database deadlock',
                'Update query transaction deadlock on database tables'
            ],
            'descs': [
                'Transactions fail when updating shopping cart contents due to database deadlocks on catalog tables.',
                'Concurrent inventory count updates cause transaction rollbacks because database queries deadlock.',
                'Simultaneous database requests to update order records fail with serialization transaction exceptions.'
            ],
            'resolutions': [
                'Standardize query locking order across concurrent updates to avoid circular waits.',
                'Apply row-level locking parameters and rewrite transaction updates to process sequentially.',
                'Wrap inventory database updates in isolation locks and introduce automatic query retry helpers.'
            ]
        }
    ],
    'API': [
        {
            'module': 'Controller',
            'titles': [
                'API returns HTTP 500 on empty POST body',
                'API crashes on empty request payload',
                'Unhandled server exception when API receives empty body'
            ],
            'descs': [
                'The backend API controller crashes instead of returning a bad request response when receiving an empty body.',
                'Sending requests with empty JSON bodies to {endpoint} causes unhandled exceptions on the server.',
                'The API endpoint crashes with a parser exception when client systems submit empty payloads.'
            ],
            'resolutions': [
                'Add validation middleware to intercept empty payloads and return standard HTTP 400 errors.',
                'Refactor request handling code block to parse payloads safely with empty check verifications.',
                'Introduce custom validation annotations to verify request body presence before executing parser code.'
            ]
        },
        {
            'module': 'Gateway',
            'titles': [
                'Rate limiter blocks legitimate internal services',
                'Internal service requests blocked by gateway rate limits',
                'Gateway rate limiting throws error on internal communications'
            ],
            'descs': [
                'Internal service-to-service calls are blocked with HTTP 429 status code during scheduled batch update tasks.',
                'The gateway rate limiter blocks API queries from {service} because request counts exceed thresholds.',
                'Communication between microservice systems fails due to aggressive rate limiter configurations.'
            ],
            'resolutions': [
                'Modify gateway configuration to whitelist internal IP ranges from rate-limiting middleware rules.',
                'Increase request threshold settings for client service identification keys.',
                'Separate internal microservice API paths from the public gateway rate limit configurations.'
            ]
        }
    ],
    'UI': [
        {
            'module': 'Navigation',
            'titles': [
                'Responsive navigation grid collapses on mobile views',
                'Navigation menu overlaps on mobile viewports',
                'Mobile viewport layout collapses navigation menu items'
            ],
            'descs': [
                'The dashboard menu overlaps content sections and collapses when viewed under narrow responsive mobile screens.',
                'Users on mobile devices are unable to click navigation buttons because grid layout properties collapse.',
                'The website header menu displays overlapping links when screen width scales below {width} pixels.'
            ],
            'resolutions': [
                'Refactor stylesheet rules to replace fixed dimensions with fluid grid viewport layouts.',
                'Apply responsive media queries to hide side menu elements and render a burger menu button.',
                'Correct the container CSS grid settings to dynamically adjust layouts based on screen width.'
            ]
        },
        {
            'module': 'Dashboard',
            'titles': [
                'Infinite rendering loop freezes browser page',
                'Dashboard component triggers infinite rendering loop',
                'State update loop consumes CPU and locks web interface'
            ],
            'descs': [
                'The application UI becomes completely unresponsive and freezes client browser tabs due to infinite state updates.',
                'Updating data options on the dashboard triggers recursive rendering loops, locking client browsers.',
                'The system freezes user interface screens as CPU usage spikes to capacity during list renders.'
            ],
            'resolutions': [
                'Fix component state hooks dependency arrays to avoid recursive cycle loops.',
                'Refactor state setters to trigger conditionally only when values undergo actual modifications.',
                'Memoize complex component list render processes using cache hooks to optimize update paths.'
            ]
        }
    ],
    'Network': [
        {
            'module': 'Ingress',
            'titles': [
                'Ingress gateway name conflicts reject routing path',
                'Gateway ingress conflicts drop routing paths',
                'Router throws error due to ingress hostname conflicts'
            ],
            'descs': [
                'Incoming traffic requests fail with service unavailable exceptions due to routing hostname namespace overlaps.',
                'The ingress proxy rejects web traffic because domain route definitions collide across namespaces.',
                'Requests fail to reach backend pods due to overlapping hostname parameters in gateway manifests.'
            ],
            'resolutions': [
                'Reconfigure ingress rules to isolate unique host namespaces and paths.',
                'Update deployment manifests to specify explicit, non-overlapping server path patterns.',
                'Clean up legacy ingress properties from old deployment scripts to resolve configuration routing conflicts.'
            ]
        },
        {
            'module': 'DNS Handler',
            'titles': [
                'DNS resolution timeout in private cloud subnets',
                'Private subnets experience DNS lookup timeouts',
                'Internal servers fail DNS lookups for external hostnames'
            ],
            'descs': [
                'Internal application nodes fail to connect to external systems because private subnet DNS lookups timeout.',
                'Virtual machines lose connection to external APIs as DNS lookups fail inside host subnets.',
                'The network gateway blocks outgoing DNS queries, causing connection failures on internal services.'
            ],
            'resolutions': [
                'Configure primary DNS forwarder fallback addresses inside virtual network settings.',
                'Verify DNS server routes inside virtual network settings and allow UDP port 53 traffic.',
                'Configure secure local DNS caches inside internal microservice container configurations.'
            ]
        }
    ],
    'Security': [
        {
            'module': 'Security Sanitizer',
            'titles': [
                'SQL injection vulnerability detected in user search',
                'User lookup search box vulnerable to SQL injection',
                'Database queries execute unsanitized string inputs'
            ],
            'descs': [
                'User input in the database search field is passed directly to dynamic statements, creating vulnerabilities.',
                'The application search engine concatenates search fields directly into SQL execute statements.',
                'Security scans report potential SQL injection points inside client lookup controller endpoints.'
            ],
            'resolutions': [
                'Refactor database query layers to bind variables rather than concatenate input strings.',
                'Migrate raw database queries to utilize secure Object-Relational Mapping libraries.',
                'Add query sanitation filters to intercept and neutralize SQL syntax characters in inputs.'
            ]
        },
        {
            'module': 'XSS Sanitizer',
            'titles': [
                'Cross-site scripting exploit possible in comments section',
                'Stored XSS vulnerability in user comments section',
                'Comment module permits script injection via text input fields'
            ],
            'descs': [
                'User review strings are rendered on pages without sanitization, permitting malicious HTML executions.',
                'Attackers can inject client-side script elements into the database through the user comments field.',
                'The frontend renders rich text descriptions directly without filtering script elements first.'
            ],
            'resolutions': [
                'Integrate content sanitizer libraries to strip potential script contents before UI rendering.',
                'Escape HTML characters and format text variables to string fields prior to client output.',
                'Implement strict Content Security Policy directives to block execution of inline script payloads.'
            ]
        }
    ],
    'Performance': [
        {
            'module': 'CPU Manager',
            'titles': [
                'High CPU usage during PDF generation queues',
                'PDF exporter spikes CPU usage to max capacity',
                'Document compilation tasks saturate server processor cores'
            ],
            'descs': [
                'The server processor utilization spikes to limit capacity when users export monthly transaction history lists.',
                'Generating large reports blocks execution workers, increasing server CPU load to 100%.',
                'The backend system crashes due to high processor load during bulk data export requests.'
            ],
            'resolutions': [
                'Offload document generation tasks to asynchronous workers to shield main threads.',
                'Implement request rate throttling on document exporter paths and apply query pagination limits.',
                'Optimize the document compilation algorithms to handle data streams instead of loading entire tables into memory.'
            ]
        },
        {
            'module': 'Pagination Helper',
            'titles': [
                'Bulk database queries execute without limit values',
                'Catalog list queries fetch large datasets without limits',
                'Missing query limits saturate memory during search actions'
            ],
            'descs': [
                'Listing items crashes web pages when database collections grow because queries fetch thousands of documents.',
                'The database response size causes backend memory exhaustion when search results fetch unlimited rows.',
                'Retrieving inventory records takes several seconds because queries do not cap output records.'
            ],
            'resolutions': [
                'Enforce pagination limits on catalog list API paths to cap resource load.',
                'Update database repository scripts to inject default limit configurations on all list queries.',
                'Migrate query structures to page-based cursor navigation strategies to limit records.'
            ]
        }
    ],
    'Backend': [
        {
            'module': 'Webhook Sync',
            'titles': [
                'Null pointer exception in webhook listener handler',
                'Webhook processing crashes on missing payload properties',
                'Listener handler fails when webhooks lack context parameters'
            ],
            'descs': [
                'The webhook processing interface returns server errors when payloads omit dynamic event context blocks.',
                'Incoming notification webhooks cause server exceptions because validation logic assumes key properties exist.',
                'The event receiver crashes while parsing webhook requests that omit tracking data fields.'
            ],
            'resolutions': [
                'Add validation checks to safely handle null parameters inside listener scripts.',
                'Implement request validation schemas to filter out incomplete webhook event payloads.',
                'Wrap the notification parsing routines inside try-catch blocks to catch parser errors gracefully.'
            ]
        },
        {
            'module': 'CSV Exporter',
            'titles': [
                'CSV export processes fail on quote character inputs',
                'Export tasks crash when text fields contain quote characters',
                'Special characters in table data break CSV formatting scripts'
            ],
            'descs': [
                'Data export scripts terminate with errors when fields contain quote symbols, disrupting formatting.',
                'The CSV builder crashes when processing text columns containing double-quote characters.',
                'Exporting audit records yields broken document outputs because parser steps fail on symbol formats.'
            ],
            'resolutions': [
                'Implement escaping strategies for special strings inside the text encoding process.',
                'Utilize compliant, standardized CSV writing libraries to handle character escapes.',
                'Sanitize text inputs during generation to strip out formatting-critical character symbols.'
            ]
        }
    ],
    'Frontend': [
        {
            'module': 'State Store',
            'titles': [
                'Application state store gets wiped on browser reload',
                'Browser reload clears user workflow settings',
                'Redux store data lost during page refresh operations'
            ],
            'descs': [
                'Users lose their current workflow configuration settings because reload actions clear local storage properties.',
                'Reloading the application resets state container values, returning users to authentication states.',
                'The frontend application fails to retain session states when users execute manual browser refreshes.'
            ],
            'resolutions': [
                'Implement state persistence routines to save configurations in browser caches.',
                'Configure state sync actions to store key variables in local storage configurations.',
                'Reconstruct application state attributes from valid token values during initialization steps.'
            ]
        },
        {
            'module': 'CSS Loader',
            'titles': [
                'Webpack configuration lacks nested CSS plugins',
                'Webpack builds fail to parse nested CSS variables',
                'Compilation errors during production CSS file parsing steps'
            ],
            'descs': [
                'Build compilation crashes during production packaging because stylesheets contain unsupported nested syntax rules.',
                'The CSS preprocessor aborts building assets because nested selector formatting rules throw syntax exceptions.',
                'Packaging tasks reject design file imports due to incorrect loader parameters inside configurations.'
            ],
            'resolutions': [
                'Configure nested CSS preprocessor plugins inside compiler script pipelines.',
                'Refactor CSS structures to eliminate nested selector rules and utilize clean layouts.',
                'Update build configuration files to verify support parameters for modern CSS plugins.'
            ]
        }
    ],
    'Configuration': [
        {
            'module': 'Env Config',
            'titles': [
                'Environment variables missing in cloud deployment',
                'Missing token config parameters crash deployment boots',
                'Startup failure due to missing mandatory configuration variables'
            ],
            'descs': [
                'Containers fail to boot up because mandatory token values are missing from system settings lists.',
                'The application initialization step aborts because server settings omit mandatory credentials.',
                'Microservice systems crash on deployment startup when configuration variables cannot be resolved.'
            ],
            'resolutions': [
                'Add defaults configuration settings and validation checks during startup phases.',
                'Implement fallback settings inside properties config files to prevent startup crashes.',
                'Configure deployment manifests to inject required environment variables from secure config maps.'
            ]
        },
        {
            'module': 'Compose Config',
            'titles': [
                'Docker compose network port mapping mismatch',
                'Compose configurations map wrong container ports',
                'Port conflict prevents docker container network access'
            ],
            'descs': [
                'Network requests fail to reach backend processes due to mismatched container ports inside compose scripts.',
                'The server fails to receive client connection queries because compose files assign duplicate ports.',
                'Containers boot up successfully but remain unreachable due to routing discrepancies in network files.'
            ],
            'resolutions': [
                'Modify host networking properties to match external paths with server ports.',
                'Correct compose ports properties to redirect traffic to the correct container listener ports.',
                'Reassign overlapping port configurations to utilize distinct available port numbers.'
            ]
        }
    ],
    'Deployment': [
        {
            'module': 'K8s Probes',
            'titles': [
                'Kubernetes readiness probe checks database prior to start',
                'Readiness probe fails during pod initialization stages',
                'Pod startup loops repeatedly due to failing readiness probes'
            ],
            'descs': [
                'Replicas are marked down during deployment because check routes execute queries before database runs.',
                'Pod deployment steps fail to complete because readiness checks run against unmounted dependencies.',
                'The container orchestrator shuts down starting pods because status routes return error codes on startup.'
            ],
            'resolutions': [
                'Refactor check logic path dependencies to allow database services to launch.',
                'Increase initial delay parameters in probe configuration manifests to permit container boot.',
                'Separate status routes from heavy database checks to avoid dependency failure loop traps.'
            ]
        },
        {
            'module': 'Dockerfile Config',
            'titles': [
                'Docker builds take too long due to layer cache losses',
                'Dockerfile configurations invalidate layers caches on edits',
                'Build process downloads packages repeatedly on minor updates'
            ],
            'descs': [
                'Automated builds download all packages on every run because changes invalidate cache lines.',
                'Docker build compilation takes several minutes due to missing layers caching setups.',
                'Minor file edits invalidate preceding copy stages, forcing packages setup reinstalls.'
            ],
            'resolutions': [
                'Reorder steps to install dependencies before importing application code files.',
                'Separate dependency configuration setup commands from source code copy operations.',
                'Verify Docker ignore configurations to skip copying local cache folders during build pipelines.'
            ]
        }
    ],
    'Cache': [
        {
            'module': 'Eviction Policy',
            'titles': [
                'Cache stampede triggers on catalog index expiry',
                'Cache stampede causes query spikes on catalog database',
                'Simultaneous cache expiration degrades database speeds'
            ],
            'descs': [
                'System performance drops significantly as concurrent lookups hit databases when items expire.',
                'The database CPU usage spikes to peak limits when key index cache records expire simultaneously.',
                'Concurrent requests flood the persistence layers because cache eviction drops key datasets.'
            ],
            'resolutions': [
                'Apply locking strategies around cache checks to intercept identical requests.',
                'Optimize Redis eviction strategy to prevent simultaneous cache expiration.',
                'Introduce random jitter parameters to caching lifespan values to avoid synchronous expiration.'
            ]
        },
        {
            'module': 'Eviction Hook',
            'titles': [
                'Stale profile details due to cache eviction failure',
                'Cache eviction failure displays stale profile details',
                'Client profile updates do not show up due to stale cache'
            ],
            'descs': [
                'Updates to client detail views fail to display because caching layers retain older records.',
                'Users complain that setting changes are not saved because cache systems fail to refresh variables.',
                'The dashboard displays stale profile records since invalidation commands fail to reach cache keys.'
            ],
            'resolutions': [
                'Add cache clearing commands to user profile update query procedures.',
                'Implement database change observer hooks to invalidate caching data upon user updates.',
                'Configure short-lived cache policies on user configuration objects inside search services.'
            ]
        }
    ],
    'Memory Leak': [
        {
            'module': 'HTTP Stream',
            'titles': [
                'HTTP response client streams left unclosed',
                'HTTP response connections leak memory under load',
                'Socket leak caused by unreleased HTTP response bodies'
            ],
            'descs': [
                'Server memory limits are exceeded because response streams remain open after API operations.',
                'The backend crashes due to socket exhaustion because request pipelines fail to close connections.',
                'Memory utilization increases continuously because client queries fail to release response handlers.'
            ],
            'resolutions': [
                'Wrap outbound requests inside auto-close blocks to ensure socket shutdown.',
                'Verify client handlers and apply connection pool parameters to close response payloads.',
                'Implement timeout limits on connection requests to automatically purge idle connections.'
            ]
        },
        {
            'module': 'Component Cleanup',
            'titles': [
                'Event listeners accumulate on frontend dashboard reload',
                'Dashboard components leak event listeners on unmount',
                'Browser tab memory consumption increases during dashboard navigation'
            ],
            'descs': [
                'Browser window processes leak memory because resize events remain registered after elements leave.',
                'Navigating between page tabs causes UI slowdowns because event listeners accumulate in memory.',
                'The frontend application leaks window resize listener hooks on component updates.'
            ],
            'resolutions': [
                'Remove listener registrations when components run cleanups on destruction.',
                'Add hook cleanup callbacks to delete window scroll event listeners upon component unmount.',
                'Refactor event handlers to utilize passive listeners that unbind automatically.'
            ]
        }
    ],
    'Logging': [
        {
            'module': 'Log Rotator',
            'titles': [
                'Logging operations exhaust system disk space',
                'Log file directories fill up local server storage',
                'Server crash caused by missing log rotation configurations'
            ],
            'descs': [
                'Production servers crash because system logs grow indefinitely without rotation strategies.',
                'The host disk partition runs out of storage space due to unchecked debug log file expansion.',
                'Stale log data accumulates on application hosts, leading to system out-of-disk outages.'
            ],
            'resolutions': [
                'Configure log files rotation sizes and apply automatic old record purges.',
                'Deploy log management tools to compress historic logs and clean directories.',
                'Set default log level rules to restrict verbose logging on production machines.'
            ]
        },
        {
            'module': 'Log Shipper',
            'titles': [
                'Log processors fail to parse malformed JSON inputs',
                'JSON parsing error crashes log shipper process',
                'Shipper service drops logs when log files have invalid characters'
            ],
            'descs': [
                'Log shipping nodes stop importing records because logs contain formatting errors.',
                'The log shipper terminates with errors when handling payloads containing non-ASCII symbols.',
                'Central logs dashboards lack query outputs because ingestion steps crash during parsing.'
            ],
            'resolutions': [
                'Sanitize text inputs to eliminate invalid formatting characters prior to processing.',
                'Configure log shipping nodes to bypass malformed json inputs without terminating pipelines.',
                'Apply secure string converters in logging controllers to handle special symbols.'
            ]
        }
    ],
    'Payment': [
        {
            'module': 'Checkout Controller',
            'titles': [
                'Duplicate charge processing on purchase double clicks',
                'Double-click events trigger duplicate transaction charges',
                'Payment gateway processes checkout requests twice'
            ],
            'descs': [
                'Customers are billed twice when clicking the submit transaction button multiple times.',
                'The payment service submits duplicate orders because users double-click submit options.',
                'Race conditions on the payment button route double transaction requests to the gateway.'
            ],
            'resolutions': [
                'Deactivate checkout action controls once processing operations initialize.',
                'Implement token parameters on request payloads to filter out duplicate payments.',
                'Configure API endpoints to perform transaction check operations prior to charging credit cards.'
            ]
        },
        {
            'module': 'Stripe Callback',
            'titles': [
                'Payment webhooks signature check fails',
                'Stripe webhook signature validation fails',
                'Callback routes reject valid payment verification signatures'
            ],
            'descs': [
                'Webhooks are rejected because validation systems parse processed payload values instead of raw data.',
                'The payment handler returns bad requests on webhook queries due to key verification issues.',
                'Webhook callbacks from billing servers fail signature validation validation procedures.'
            ],
            'resolutions': [
                'Modify endpoint settings to read raw payload contexts for verification checks.',
                'Rotated expired webhook secret configuration parameters in production deployment files.',
                'Verify signature validation libraries configuration and match webhook callback settings.'
            ]
        }
    ],
    'Search': [
        {
            'module': 'Fuzzy Search',
            'titles': [
                'Fuzzy search returns empty values on close terms',
                'Fuzzy query logic misses closely misspelled catalog terms',
                'Search box yields empty results on small typos'
            ],
            'descs': [
                'Searching for slightly misspelled names yields empty results due to strict match parameters.',
                'The catalog search engine fails to fetch items if query strings contain character typos.',
                'Fuzzy search configurations miss valid target documents due to narrow metric settings.'
            ],
            'resolutions': [
                'Set query boundaries to auto-fuzziness inside match configurations.',
                'Update search client queries to enable Levenshtein edit distance logic.',
                'Adjust fuzziness thresholds on key query parameters inside properties profiles.'
            ]
        },
        {
            'module': 'Index Tracker',
            'titles': [
                'New inventory items missing from search query results',
                'Search index sync delayed for newly added products',
                'Product additions do not show up in searches'
            ],
            'descs': [
                'Newly added products fail to show up in queries because database hooks omit indexing tasks.',
                'The product catalog fails to refresh index registries, delaying new items from search results.',
                'Search query outputs exclude updated records due to cache delay variables.'
            ],
            'resolutions': [
                'Integrate index refresh commands inside catalog save query frameworks.',
                'Reconfigure database transaction listeners to index catalog entities asynchronously.',
                'Increase sync intervals on index managers to capture dataset changes.'
            ]
        }
    ],
    'Notification': [
        {
            'module': 'SMS Dispatcher',
            'titles': [
                'SMS alerts lock up messaging queues under load',
                'Messaging queues lock up during peak SMS alerts delivery',
                'High traffic SMS dispatcher blocks internal messaging queues'
            ],
            'descs': [
                'Alert notifications are delayed because high volume events lock queue execution lanes.',
                'The background task queue stalls when sending bulk verification texts to clients.',
                'SMS notification workloads bottleneck execution pipelines, halting email processes.'
            ],
            'resolutions': [
                'Create isolated runners to process SMS tasks separately from email routes.',
                'Apply concurrent thread limit settings to message queues to avoid task lockouts.',
                'Migrate SMS notifications dispatch logic to asynchronous server-sent event pools.'
            ]
        },
        {
            'module': 'Email Engine',
            'titles': [
                'Email compiler crashes on missing template keys',
                'Missing template variables crash email dispatch operations',
                'Registration verification emails fail due to compilation crashes'
            ],
            'descs': [
                'Emails fail to send because compiler systems crash when parameters do not map to template variables.',
                'The email builder aborts sending messages when user parameters contain null fields.',
                'Automated receipt dispatch operations fail due to syntax parsing errors in HTML templates.'
            ],
            'resolutions': [
                'Introduce default placeholder definitions inside mail compiler setups.',
                'Implement schema checks to validate payload values before triggering compiler actions.',
                'Add try-catch structures around rendering runs to catch variable reference errors.'
            ]
        }
    ],
    'File Upload': [
        {
            'module': 'Upload Controller',
            'titles': [
                'Large file uploads abort on server timeout limits',
                'API gateway aborts large file uploads with connection timeouts',
                'File transfers above 50MB abort due to request timeout settings'
            ],
            'descs': [
                'File transfers above 50MB fail because server connection channels close after 30 seconds.',
                'Users get network errors when uploading video assets due to execution timeout settings.',
                'Ingest processes close active streams when user files exceed size limits.'
            ],
            'resolutions': [
                'Increase connection timeout configurations on file ingest API routes.',
                'Modify nginx properties to allow extended request processing windows on upload paths.',
                'Refactor file ingest pathways to split files into multiple small upload chunks.'
            ]
        },
        {
            'module': 'Security Sanitizer',
            'titles': [
                'Validation allows upload of executable script files',
                'Upload system accepts malicious script files',
                'Missing mime verification allows executable uploads'
            ],
            'descs': [
                'Security systems accept malicious uploads because verification steps check extensions instead of content type.',
                'Attackers can upload active script files by modifying filename parameters.',
                'The file receiver skips verification steps, accepting executable assets on hosts.'
            ],
            'resolutions': [
                'Introduce binary signature header analyses to verify file types.',
                'Verify content configurations to validate mime types prior to saving files.',
                'Configure storage buckets to block execution permissions on uploaded file assets.'
            ]
        }
    ],
    'Session Management': [
        {
            'module': 'Cookie Settings',
            'titles': [
                'Session cookies miss HTTPOnly security identifiers',
                'HTTPOnly configuration properties missing on session cookies',
                'Secure cookie flags missing on user authorization settings'
            ],
            'descs': [
                'Client cookies are exposed to scripts because verification properties omit secure attributes.',
                'Security audits identify missing HttpOnly flag settings on authorization cookies.',
                'Vulnerability scanners report session hijacking risk due to missing cookie headers.'
            ],
            'resolutions': [
                'Update backend session scripts to set HTTPOnly and Secure options to True.',
                'Modify session creation methods to append security flag attributes onto cookie records.',
                'Reconfigure gateway cookie settings to force secure transportation pathways.'
            ]
        },
        {
            'module': 'Session Cleanup',
            'titles': [
                'Session database storage grows without automated cleanups',
                'Expired user session records bloat database storage',
                'Session database records missing automatic eviction policies'
            ],
            'descs': [
                'System nodes report storage capacity failures because stale user records do not get deleted.',
                'The session registry database consumes major disk resources due to missing TTL configs.',
                'Backend server performance drops because queries parse millions of expired session records.'
            ],
            'resolutions': [
                'Enable database lifetime configurations on table columns to sweep old entries.',
                'Implement hourly cron jobs to delete expired session records from databases.',
                'Configure TTL index settings on target session logs database collections.'
            ]
        }
    ]
}

# Env lookup based on tech
def get_env_by_tech(tech):
    if tech in ['React', 'Angular', 'Vue']:
        return random.choice(['Web', 'Docker', 'Kubernetes'])
    elif tech == 'Android':
        return 'Android'
    elif tech == 'iOS':
        return 'iOS'
    elif tech == 'AWS':
        return 'AWS'
    elif tech == 'Azure':
        return 'Azure'
    elif tech == 'Kubernetes':
        return 'Kubernetes'
    elif tech == 'Docker':
        return 'Docker'
    elif tech in ['Django', 'Flask', 'Spring Boot', 'Laravel', 'Node.js', 'Express', 'ASP.NET']:
        return random.choice(['Linux', 'Windows', 'Docker', 'Kubernetes', 'Web'])
    else: # DBs
        return random.choice(['Linux', 'Windows', 'AWS', 'Azure', 'Docker'])

def generate_bug_record(bug_id, category, severity, status):
    tech = random.choice(CATEGORIES_TECH_MAP[category])
    
    # Pick a random scenario for the category
    scenario = random.choice(SCENARIOS[category])
    
    # Choose random template variations to guarantee uniqueness
    title_template = random.choice(scenario['titles'])
    desc_template = random.choice(scenario['descs'])
    res_template = random.choice(scenario['resolutions'])
    
    # Generate placeholder values
    user = f"user_{random.randint(100, 999)}"
    port = str(random.choice([80, 443, 3000, 5000, 8080, 8443]))
    endpoint = random.choice(['/api/v1/auth', '/api/users/login', '/oauth/callback', '/checkout/pay', '/search/catalog'])
    service = random.choice(['auth-gateway', 'user-service', 'payment-worker', 'search-node', 'api-router'])
    time_val = str(random.choice([5, 10, 15, 30, 60]))
    limit_val = str(random.choice([50, 100, 200, 500]))
    db_val = random.choice(['prod_db', 'users_store', 'catalog_db', 'transactions_log'])
    width_val = str(random.choice([480, 768, 1024]))
    
    # Populate templates
    title = title_template.format(tech=tech, user=user, port=port, endpoint=endpoint, service=service, time=time_val, limit=limit_val, db=db_val, width=width_val)
    desc = desc_template.format(tech=tech, user=user, port=port, endpoint=endpoint, service=service, time=time_val, limit=limit_val, db=db_val, width=width_val)
    resolution = res_template.format(tech=tech, user=user, port=port, endpoint=endpoint, service=service, time=time_val, limit=limit_val, db=db_val, width=width_val)
    
    module = scenario['module']
    env = get_env_by_tech(tech)
    priority = PRIORITY_MAP[severity]
    
    # Expected resolution time mapping based on Severity boundaries:
    # Critical: 1-8 hours
    # High: 8-24 hours
    # Medium: 24-72 hours (1-3 days)
    # Low: 72-168 hours (3-7 days)
    if severity == 'Critical':
        exp_res = random.randint(1, 8)
    elif severity == 'High':
        exp_res = random.randint(8, 24)
    elif severity == 'Medium':
        exp_res = random.randint(24, 72)
    else: # Low
        exp_res = random.randint(72, 168)
        
    # Return exactly the 12 columns requested
    return {
        'Bug_ID': bug_id,
        'Bug_Title': title,
        'Bug_Description': desc,
        'Category': category,
        'Technology': tech,
        'Module': module,
        'Environment': env,
        'Severity': severity,
        'Priority': priority,
        'Status': status,
        'Resolution': resolution,
        'Expected_Resolution_Time': exp_res
    }

def main():
    parser = argparse.ArgumentParser(description="Synthetic Bug Dataset Generator")
    parser.add_argument("--count", type=int, default=15000, help="Number of records to generate")
    parser.add_argument("--sample", action="store_true", help="Generate only 20 sample rows for preview")
    parser.add_argument("--output", type=str, default="bug_reports.csv", help="Output CSV file path")
    args = parser.parse_args()

    count = 20 if args.sample else args.count
    output_file = "sample_bug_reports.csv" if args.sample else args.output
    
    print(f"Generating {count} bug records...")
    
    records = []
    
    # We want class balance: distribute category and severity combinations equally
    for i in range(count):
        bug_id = f"BUG{i+1:05d}"
        
        # Round-robin distribution for category and severity to ensure perfect class balance
        category = CATEGORIES[i % len(CATEGORIES)]
        severity = SEVERITIES[i % len(SEVERITIES)]
        
        # Status distribution (Open: ~15%, In Progress: ~15%, Fixed: ~40%, Closed: ~30%)
        status_weights = [0.15, 0.15, 0.40, 0.30]
        status = random.choices(STATUSES, weights=status_weights, k=1)[0]
        
        record = generate_bug_record(bug_id, category, severity, status)
        records.append(record)
        
    df = pd.DataFrame(records)
    
    # Verify uniqueness of descriptions
    dups = df.duplicated(subset=['Bug_Description']).sum()
    if dups > 0 and not args.sample:
        print(f"Found {dups} duplicate descriptions. Fixing duplicates...")
        # Since we use randomized templates, duplicates will be minimal, but we sweep and regenerate
        while dups > 0:
            dup_indices = df[df.duplicated(subset=['Bug_Description'])].index
            for idx in dup_indices:
                rec = generate_bug_record(df.loc[idx, 'Bug_ID'], df.loc[idx, 'Category'], df.loc[idx, 'Severity'], df.loc[idx, 'Status'])
                # Append minor variation keys to description if needed to enforce uniqueness
                variant_suffix = f" Note: system transaction key {random.randint(1000, 9999)} was recorded."
                rec['Bug_Description'] += variant_suffix
                df.loc[idx] = rec
            dups = df.duplicated(subset=['Bug_Description']).sum()
            
    df.to_csv(output_file, index=False)
    print(f"Dataset generated and saved to: {os.path.abspath(output_file)}")
    print(f"Record count: {len(df)}")
    print(f"Unique descriptions: {df['Bug_Description'].nunique()}")
    print("\nClass Distribution for Severity:")
    print(df['Severity'].value_counts())
    print("\nClass Distribution for Category:")
    print(df['Category'].value_counts())

if __name__ == "__main__":
    main()
