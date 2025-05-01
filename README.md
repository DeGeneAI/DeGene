# DeGene - Decentralized Genome Data Storage and Analysis Platform

<img width="615" alt="9cef8cd8a3b08b40cf006bc0ef2c836" src="https://github.com/user-attachments/assets/2fda09cd-c27a-4571-92b3-08f423887edf" />

DeGene is a decentralized platform for secure genome data storage and analysis, built on the Solana blockchain. The platform combines the power of blockchain technology, IPFS distributed storage, and advanced genomic analysis capabilities.
CA: 7gPY6r1peEmb5fKwoz59qpWQUZZ8dxghC4u4yAHhpump
## Features

### Core Features
- **Secure Authentication**
  - JWT-based authentication system
  - Rate limiting protection
  - Role-based access control

### Genome Management
- **Data Storage**
  - Secure genome data storage using IPFS
  - Metadata management
  - Data encryption support

- **Blockchain Integration**
  - Genome data ownership records on Solana
  - Transaction history tracking
  - Ownership verification

- **Access Control**
  - Fine-grained access control
  - Data sharing capabilities
  - Permission management

### Genome Analysis Features
- **Sequence Analysis**
  - GC content calculation
  - Sequence length analysis
  - N-content analysis
  - Quality score assessment
  - Sequence similarity comparison

- **Visualization Tools**
  - GC content distribution plots
  - Sequence length distribution plots
  - Quality score distribution plots
  - Sequence alignment visualization

- **Batch Processing**
  - Asynchronous batch processing
  - Multi-threading support
  - Automatic batch splitting
  - Result visualization generation

## Comprehensive User Guide

### 1. System Requirements

#### Hardware Requirements
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 100GB+ SSD recommended
- Network: Stable internet connection

#### Software Requirements
- Python 3.8+
- Node.js 14+
- Solana CLI tools
- IPFS Desktop or daemon
- Git

### 2. Development Environment Setup

#### 2.1 Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2.2 Solana Setup
```bash
# Install Solana CLI tools
sh -c "$(curl -sSfL https://release.solana.com/v1.17.0/install)"

# Configure Solana CLI
solana config set --url https://api.devnet.solana.com

# Create new keypair
solana-keygen new --outfile ~/.config/solana/devnet.json

# Airdrop SOL for testing
solana airdrop 2 $(solana address) --url https://api.devnet.solana.com
```

#### 2.3 IPFS Setup
```bash
# Install IPFS
wget https://dist.ipfs.io/go-ipfs/v0.12.0/go-ipfs_v0.12.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.12.0_linux-amd64.tar.gz
cd go-ipfs
sudo bash install.sh

# Initialize IPFS
ipfs init

# Start IPFS daemon
ipfs daemon
```

### 3. Application Configuration

#### 3.1 Environment Variables
Create `.env` file in project root:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# JWT Configuration
JWT_SECRET=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Solana Configuration
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_WS_URL=wss://api.devnet.solana.com
SOLANA_KEYPAIR_PATH=~/.config/solana/devnet.json

# IPFS Configuration
IPFS_API_URL=http://localhost:5001
IPFS_GATEWAY_URL=http://localhost:8080

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/degene
```

#### 3.2 Database Setup
```bash
# Install PostgreSQL (Ubuntu)
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
postgres=# CREATE DATABASE degene;
postgres=# CREATE USER degeneuser WITH PASSWORD 'password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE degene TO degeneuser;
```

### 4. Running the Application

#### 4.1 Development Mode
```bash
# Start API server
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/docs
```

#### 4.2 Production Mode
```bash
# Start with Gunicorn
gunicorn src.api.server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 5. API Usage Examples

#### 5.1 User Management

##### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "name": "Test User"
  }'
```

##### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

#### 5.2 Genome Management

##### Upload Genome
```bash
curl -X POST http://localhost:8000/api/genome/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@genome_data.fastq" \
  -F 'metadata={
    "name": "Sample Genome",
    "description": "Test genome data",
    "source": "Laboratory X",
    "date": "2024-01-01"
  }'
```

##### List Genomes
```bash
curl -X GET http://localhost:8000/api/genome/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

##### Get Specific Genome
```bash
curl -X GET http://localhost:8000/api/genome/GENOME_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 6. Common Operations

#### 6.1 Data Backup
```bash
# Backup database
pg_dump -U degeneuser degene > backup.sql

# Backup IPFS data
ipfs pin ls --type recursive > ipfs_pins.txt
```

#### 6.2 System Monitoring
```bash
# Check API server status
curl http://localhost:8000/api/health

# Monitor logs
tail -f logs/degene.log

# Check IPFS status
ipfs swarm peers
```

#### 6.3 Troubleshooting
```bash
# Clear API server cache
rm -rf __pycache__

# Reset IPFS connection
ipfs shutdown
ipfs daemon --init

# Check Solana connection
solana cluster-version
```

### 7. Security Best Practices

#### 7.1 API Security
- Use strong passwords
- Regularly rotate JWT secrets
- Enable rate limiting
- Configure CORS properly
- Use HTTPS in production

#### 7.2 Data Security
- Encrypt sensitive data
- Regular security audits
- Monitor access logs
- Implement backup strategy

#### 7.3 Blockchain Security
- Secure key management
- Regular transaction monitoring
- Multiple signature support
- Network security monitoring

### 8. Genome Analysis Features

#### 8.1 Sequence Analysis
```python
from src.analysis.genome_analyzer import GenomeAnalyzer

analyzer = GenomeAnalyzer()
result = analyzer.analyze_sequence("ATCG...")
print(f"GC Content: {result['gc_content']}")
print(f"Length: {result['length']}")
print(f"Quality Score: {result['quality_score']}")
```

#### 8.2 Visualization
```python
from src.visualization.genome_visualizer import GenomeVisualizer

visualizer = GenomeVisualizer()
gc_plot = visualizer.plot_gc_content(0.45)
# Save or display the plot
```

#### 8.3 Batch Processing
```python
from src.processing.batch_processor import BatchProcessor

processor = BatchProcessor(max_workers=4)
results = await processor.process_batch(sequences)
visualizations = await processor.generate_visualizations(results)
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### Genome Management
- `POST /api/genome/upload` - Upload genome data
- `GET /api/genome/list` - List user's genomes
- `GET /api/genome/{genome_id}` - Get specific genome
- `DELETE /api/genome/{genome_id}` - Delete genome

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DeGene.git
cd DeGene
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
uvicorn src.api.server:app --reload
```

## Configuration

Key configuration items in `.env`:
```
JWT_SECRET=your-secret-key
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PRIVATE_KEY=your-private-key
IPFS_NODE_URL=your-ipfs-node
```

## Development

### Project Structure
```
src/
├── api/
│   ├── middleware/
│   │   ├── auth.py
│   │   └── rate_limit.py
│   ├── models/
│   │   ├── user.py
│   │   └── genome.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── genome.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── genome.py
│   ├── services/
│   │   ├── blockchain.py
│   │   └── storage.py
│   └── server.py
├── blockchain/
└── genomics/
```

## Security

- JWT-based authentication
- Rate limiting to prevent abuse
- CORS configuration for API security
- Encrypted data storage
- Blockchain-based ownership verification

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the GPL-3.0 - see the LICENSE file for details.
