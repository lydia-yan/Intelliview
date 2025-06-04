"""
Content extraction and analysis for portfolio websites
"""

import re
from typing import List, Set
from bs4 import BeautifulSoup, Comment

from backend.config import PortfolioConfig
from .data_models import PortfolioData, ProjectInfo
from .exceptions import PortfolioContentError

class PortfolioContentExtractor:
    """Extract structured content from portfolio HTML"""
    
    def __init__(self):
        self.config = PortfolioConfig()
        
        self.tech_keywords = {
            # Programming Languages
            'javascript', 'js', 'typescript', 'ts', 'python', 'java', 'c++', 'cpp', 'c#', 'csharp', 
            'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'dart',
            'c', 'objective-c', 'vb.net', 'f#', 'haskell', 'clojure', 'elixir', 'erlang', 'lua',
            
            # Web Technologies
            'html', 'css', 'sass', 'scss', 'less', 'bootstrap', 'tailwind', 'react', 'vue', 'angular',
            'svelte', 'ember', 'backbone', 'jquery', 'next.js', 'nuxt.js', 'gatsby', 'webpack', 'vite',
            'parcel', 'rollup', 'babel', 'eslint', 'prettier', 'jest', 'cypress', 'selenium',
            
            # Backend & Frameworks
            'node', 'nodejs', 'express', 'koa', 'fastify', 'django', 'flask', 'fastapi', 'spring',
            'springboot', 'laravel', 'symfony', 'rails', 'sinatra', 'gin', 'echo', 'fiber',
            'asp.net', 'blazor', 'strapi', 'nestjs', 'meteor',
            
            # Databases
            'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'dynamodb', 'firestore', 'firebase', 'supabase', 'neo4j', 'influxdb', 'mariadb',
            'oracle', 'sqlserver', 'couchdb', 'rethinkdb',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google-cloud', 'heroku', 'vercel', 'netlify', 'digitalocean',
            'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab-ci', 'github-actions', 'circleci',
            'terraform', 'ansible', 'vagrant', 'chef', 'puppet', 'serverless', 'lambda',
            
            # Data Science & AI/ML
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv',
            'matplotlib', 'seaborn', 'plotly', 'jupyter', 'anaconda', 'spark', 'hadoop',
            'airflow', 'dbt', 'streamlit', 'dash', 'tableau', 'powerbi', 'qlik',
            
            # Mobile Development
            'react-native', 'flutter', 'ionic', 'xamarin', 'cordova', 'phonegap', 'nativescript',
            'android', 'ios', 'xcode', 'android-studio',
            
            # Design & Creative
            'figma', 'sketch', 'adobe-xd', 'invision', 'photoshop', 'illustrator', 'indesign',
            'after-effects', 'premiere', 'blender', 'maya', '3ds-max', 'cinema4d', 'unity',
            'unreal', 'substance', 'zbrush', 'procreate', 'canva',
            
            # Version Control & Tools
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial', 'perforce',
            'jira', 'confluence', 'trello', 'asana', 'notion', 'slack', 'discord',
            
            # Testing & Quality
            'junit', 'pytest', 'mocha', 'chai', 'jasmine', 'karma', 'protractor', 'testng',
            'cucumber', 'postman', 'insomnia', 'soapui', 'jmeter', 'locust',
            
            # Game Development
            'unity3d', 'unreal-engine', 'godot', 'construct', 'gamemaker', 'phaser', 'pixi.js',
            'three.js', 'babylon.js', 'love2d', 'pygame', 'libgdx',
            
            # Blockchain & Web3
            'solidity', 'ethereum', 'bitcoin', 'blockchain', 'web3', 'metamask', 'hardhat',
            'truffle', 'ganache', 'ipfs', 'polygon', 'binance-smart-chain',
            
            # DevOps & Monitoring
            'prometheus', 'grafana', 'elk', 'logstash', 'kibana', 'splunk', 'datadog',
            'newrelic', 'sentry', 'bugsnag', 'rollbar', 'pingdom',
            
            # CMS & E-commerce
            'wordpress', 'drupal', 'joomla', 'shopify', 'magento', 'woocommerce', 'prestashop',
            'opencart', 'bigcommerce', 'strapi', 'contentful', 'sanity', 'ghost',
            
            # API & Communication
            'rest', 'graphql', 'grpc', 'soap', 'websocket', 'socket.io', 'ajax', 'fetch',
            'axios', 'curl', 'postman', 'swagger', 'openapi', 'json', 'xml', 'yaml',
            
            # Security
            'oauth', 'jwt', 'ssl', 'tls', 'https', 'encryption', 'cybersecurity', 'penetration-testing',
            'burp-suite', 'nmap', 'wireshark', 'metasploit', 'kali-linux',
            
            # Project Management & Methodologies
            'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'devops', 'ci/cd', 'tdd', 'bdd',
            'pair-programming', 'code-review', 'microservices', 'monolith', 'soa'
        }
        
    def extract_portfolio_data(self, html_content: str, url: str) -> PortfolioData:
        """
        Extract structured portfolio data from HTML content
        
        Args:
            html_content: Raw HTML content from portfolio website
            url: Original portfolio URL
            
        Returns:
            PortfolioData: Extracted and structured portfolio information
            
        Raises:
            PortfolioContentError: If content extraction fails
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Extract components
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            projects = self._extract_projects(soup)
            skills = self._extract_skills(soup)
            experience = self._extract_experience(soup)
            raw_content = self._get_clean_text(soup)
            
            return PortfolioData(
                url=url,
                title=title,
                description=description,
                projects=projects,
                skills=skills,
                experience=experience,
                raw_content=raw_content
            )
            
        except Exception as e:
            raise PortfolioContentError(url, f"Failed to extract portfolio content: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract portfolio title or owner name"""
        # Try multiple selectors for title
        for selector in self.config.PLATFORM_SELECTORS["default"]["title"]:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) < 100:  # Reasonable title length
                    return text
        
        # Fallback to page title
        title_element = soup.find('title')
        if title_element:
            return title_element.get_text(strip=True)
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract portfolio description or bio"""
        # Try multiple selectors for description
        for selector in self.config.PLATFORM_SELECTORS["default"]["description"]:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and 50 < len(text) < 1000:  # Reasonable description length
                    return text
        
        # Look for paragraphs that might be descriptions
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if 50 < len(text) < 1000 and self._is_descriptive_text(text):
                return text
        
        return ""
    
    def _extract_projects(self, soup: BeautifulSoup) -> List[ProjectInfo]:
        """Extract project information"""
        projects = []
        
        # Try multiple selectors for projects
        project_elements = []
        for selector in self.config.PLATFORM_SELECTORS["default"]["projects"]:
            project_elements.extend(soup.select(selector))
        
        # Also look for common project containers
        additional_selectors = [
            'article', '[class*="card"]', '[class*="item"]',
            '[id*="project"]', '[id*="portfolio"]', '[id*="work"]'
        ]
        for selector in additional_selectors:
            project_elements.extend(soup.select(selector))
        
        seen_projects = set()
        for element in project_elements:
            project = self._extract_single_project(element)
            if project and project.name not in seen_projects:
                projects.append(project)
                seen_projects.add(project.name)
                if len(projects) >= self.config.MAX_PROJECTS:
                    break
        
        return projects
    
    def _extract_single_project(self, element) -> ProjectInfo:
        """Extract information from a single project element"""
        # Get project name
        name = ""
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading = element.find(tag)
            if heading:
                name = heading.get_text(strip=True)
                break
        
        if not name:
            # Try other potential name sources
            name_element = element.find(['strong', 'b', '[class*="title"]', '[class*="name"]'])
            if name_element:
                name = name_element.get_text(strip=True)
        
        if not name or len(name) > 100:
            return None
        
        # Get project description
        description = ""
        paragraphs = element.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if 20 < len(text) < 500:  # Reasonable description length
                description = text
                break
        
        # Get project URL
        project_url = None
        link = element.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith(('http://', 'https://')):
                project_url = href
        
        # Extract technologies
        technologies = self._extract_technologies_from_element(element)
        
        return ProjectInfo(
            name=name,
            description=description,
            technologies=technologies,
            url=project_url
        )
    
    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract skills and technologies"""
        skills = set()
        
        # Try multiple selectors for skills
        for selector in self.config.PLATFORM_SELECTORS["default"]["skills"]:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True).lower()
                skills.update(self._extract_tech_from_text(text))
        
        # Look for skills in lists
        lists = soup.find_all(['ul', 'ol'])
        for ul in lists:
            list_text = ul.get_text().lower()
            if any(keyword in list_text for keyword in ['skill', 'tech', 'tool', 'language']):
                skills.update(self._extract_tech_from_text(list_text))
        
        # Extract from all text content
        all_text = soup.get_text().lower()
        skills.update(self._extract_tech_from_text(all_text))
        
        # Filter and limit skills
        filtered_skills = [skill for skill in skills if len(skill) > 1]
        return sorted(filtered_skills)[:self.config.MAX_SKILLS]
    
    def _extract_experience(self, soup: BeautifulSoup) -> str:
        """Extract experience or work history"""
        # Look for experience sections
        experience_keywords = ['experience', 'work', 'employment', 'career', 'background']
        
        for keyword in experience_keywords:
            # Try to find sections with experience-related content
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                parent = element.parent
                if parent:
                    section_text = parent.get_text(strip=True)
                    if 100 < len(section_text) < 2000:
                        return section_text
        
        return ""
    
    def _extract_technologies_from_element(self, element) -> List[str]:
        """Extract technology keywords from a specific element"""
        text = element.get_text().lower()
        return list(self._extract_tech_from_text(text))
    
    def _extract_tech_from_text(self, text: str) -> Set[str]:
        """Extract technology keywords from text"""
        found_tech = set()
        text_lower = text.lower()
        
        for tech in self.tech_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, text_lower):
                found_tech.add(tech.title())
        
        return found_tech
    
    def _is_descriptive_text(self, text: str) -> bool:
        """Check if text appears to be a description rather than navigation/boilerplate"""
        # Simple heuristics to identify descriptive content
        descriptive_indicators = [
            'i am', 'i\'m', 'my name', 'about me', 'developer', 'engineer',
            'experience', 'passionate', 'specialize', 'focus', 'love', 'enjoy'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in descriptive_indicators)
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Get clean text content for fallback"""
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Limit length
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        return text 