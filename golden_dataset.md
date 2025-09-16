# Gold Dataset Generation Process

This document outlines the standardized process used by the Data Team to generate the Gold Dataset. The dataset consists of high-quality, rubric-scored assessment data across multiple domains.

The goal is to create authentic, research-aligned resources suitable for training and evaluating assessment models. Each data point is a self-contained JSON file that includes the domain, a prompt, a detailed rubric, and multiple submissions graded against that rubric.

## Dataset Summary

- **Domains**: Psychology, Teaching, Accounting, IT, Engineering
- **Number of Records/Files**: 100 generated
- **Path to Dataset**: docs/golden_dataset.md

## Dataset Schema Evolution

This section tracks the major changes to the dataset's structure. The current active versions are v0.5 and v1.0, as not all datasets have been updated to include authorship classes. An example of a file conforming to the latest schema (v1.0) can be found here:
 [https://github.com/InnovAIte-Deakin/aaie-Data-Hub/blob/ab6c759768775e52ea4292321a3fa60719187645/data/curated/rub_psychology_0001.json]

| Version | Commit/PR | Change Description | Status |
|---------|-----------|-------------------|---------|
| 0.1 | N/A | Initial schema definition including domain, prompt, rubric, criteria, and submissions. | Superseded |
| 0.5 | N/A | Added weight field to rubric criteria to support numerical scoring. | Active |
| 1.0 | N/A | Added authorship and hybrid_breakdown fields to submissions to label ai, human, and hybrid content. | Active |

## Standardized Generation Workflow

The generation process follows a structured, 10-step workflow that combines manual prompt engineering with controlled automation to ensure quality and consistency.

### Step 1: Rubric Creation

- **Topic Generation**: Essay topics for a specific domain are generated using LLMs (ChatGPT, Gemini, CoPilot)
- **Rubric Adaptation**: A generic rubric structure is adapted from established academic exemplars (e.g., iRubric)
- **Finalization**: The final rubric is generated using a structured prompt. Each rubric consists of 4 to 6 criteria with five performance levels: Excellent, Good, Average, Needs Improvement, and Poor

**Important Note**: Due to time constraints, it has been agreed with the project Product Owner that a generic rubric will be used as the basis for rubric generation for Trimester 2, 2025. There is a possibility of incorporating real university rubric samples, such as Deakin's past rubrics, provided that ethical approval has been granted for the AAIE project.

### Step 2: Key-Points Generation

- **Benchmark Definition**: For each performance level, a collection of key points is generated to serve as benchmarks and guides for the subsequent steps

### Step 3: LLM Questions Generation

- **Simulating Research**: A collection of questions is generated to imitate a student's research process, ensuring balanced coverage of all rubric criteria

### Step 4: LLM Answers Collection

- **Content Generation**: The questions are fed to an LLM to generate a collection of answers. Answers for each performance level are generated in separate conversations for authentic variation

### Step 5: AI Submission Synthesis

- **Essay Generation**: The rubric and generated answers are used to produce a final, essay-style submission (~200+ words) that simulates AI-authored student writing for each performance level
- **Academic Realism**: For "Excellent" and "Good" submissions, APA-style citations and references are added

### Step 6: Feedback Generation

- **Automated Assessment**: The AI submission and rubric are provided to an LLM to generate grading and feedback for each criterion, including a qualitative comment and a numerical score

### Step 7: Rubric Weighting

- **Weight Assignment**: Weights are assigned to each criterion to reflect its importance, using either a randomized script with manual review or a standard template

### Step 8: Submission Augmentation

- **Data Enhancement**: An automated script generates additional AI submissions with mixed-performance profiles (e.g., strong analysis but weak writing) to create more realistic and diverse training data

### Step 9: Human & Hybrid Submission Creation

- **Manual Intervention**: To enrich the dataset, select AI-generated submissions are manually edited to create human and hybrid versions
- **Authorship Labeling**: All submissions are programmatically labeled with an authorship tag (ai, human, or hybrid) and a hybrid_breakdown object that specifies the authorship of each paragraph by its index

### Step 10: Quality Assurance

- **Consistency Check**: A final step involves running prompts to fix any inconsistent or unrealistic JSON outputs to ensure the final data is clean and usable

## Note on Future Process Improvement

The current generation process patches human/hybrid edits after feedback has been generated. The ideal future workflow should be re-ordered as follows:

Rubric Gen → LLM Questions → LLM Answers → Final Submission → Human Edit (Hybrid/Human) → Feedback Generation

## Collated Prompts

This section contains a master list of the prompts used at various stages of the generation workflow, organized by task.

### Step 1: Rubric Creation

```
Generate a list of essay topics for the [Domain Name] domain.
Then, create a rubric for each topic with 4-6 criteria, each with performance descriptors for:
Excellent, Good, Average, Needs Improvement, Poor.
```

### Step 2: Key-Points Generation

```
Create the key_points for each quality specifically for the submission section in the below Json and embed them in a new Json file:

[rub_domain_xxxx]
```

### Step 3: LLM Questions Generation

```
You are an undergraduate student studying [Domain Name], and you need to breakdown and research the essay components that will help you write an essay for the rubric prompt that meets the performance evaluation criteria. Generate research questions for each of the five performance levels based on the rubric criteria.

rubric:
[rub_domain_xxxx]
```

### Step 4: LLM Answers Collection

```
Answer questions:

[questions]

Provide the answers only in JSON format like below:
"llm_answers": [ "Answer 1...", "Answer 2...", ... ]
```

### Step 5: AI Submission Synthesis

```
You are an undergraduate student studying [Domain Name]; your task is to write an essay for the rubric prompt that would meet the "[LEVEL]" submission level. Use the llm_answers above to write naturally, varying transition words and avoiding robotic-sounding content. Write the completed essay and wrap it in the JSON field "final_submission", using \n\n for separating paragraphs.

[rub_domain_xxxx]
```

### Step 6: Feedback Generation

```
You are a university professor grading an essay. Provide grading (e.g., Excellent, Good) and feedback for each criterion in the rubric for the submission below. Wrap the output in a "feedback" field.

"feedback": { "c1": "Good. xxxx", "c2": "Average. xxxx", ... }
```

### Step 8: Submission Augmentation

```
You are an expert in educational assessment. Your task is to add 5 NEW submissions to an existing JSON dataset that already has weights and weighted scores.

YOUR TASK: Add exactly 5 NEW submissions with VARIED and REALISTIC quality distributions across criteria (e.g., strong analysis but weak writing).

Scoring Guidelines:
- Excellent: 90-100% of criterion weight
- Good: 75-89% of criterion weight
- Average: 60-74%
- Needs Improvement: 45-59%
- Poor: 0-44%

Input data:
[file_to_write]
```

### Step 9: Authorship Labeling

```
Update each submission with authorship classification and hybrid breakdown.
- Add "authorship": "ai", "human", or "hybrid".
- Add "hybrid_breakdown" with "ai_paragraph_indices", "human_paragraph_indices", and "notes" explaining the edits.
```

### Step 10: Quality Assurance / Fixing Inconsistent Output

```
Regenerate the "submissions" array for a rubric-based essay dataset.
Follow these rules:
- Each submission must match its rubric's descriptors.
- Scores must align with weightings.
- Quality distributions should vary (not all criteria at the same level).
- Essays should use proper academic structure (Intro, Body, Conclusion).

INPUTS:
1. RUBRIC (JSON): [file_to_write]
2. ORIGINAL SUBMISSION (to be replaced): [file_to_write]
```

## Master List of Rubrics

This section contains the list of all prompts for which rubrics have been generated, organized by domain.

### Psychology

| Rubric ID | Prompt | Schema Version |
|-----------|--------|----------------|
| rub_psychology_0001 | Critically evaluate the role of cognitive biases in human decision-making. Select at least three cognitive biases (e.g., confirmation bias, anchoring, availability heuristic) and explain how they influence decision-making in real-world scenarios (e.g., healthcare, law, relationships, consumer behavior). Discuss the psychological theories behind them and explore how awareness or mitigation strategies can improve judgment. | 1.0 |
| rub_psychology_0002 | The Diagnostic and Statistical Manual of Mental Disorders (DSM-5) is widely used in psychological diagnosis and clinical practice. Explain the purpose and structure of the DSM-5. Select one disorder, describe its diagnostic criteria, symptomology, and classification. Evaluate strengths and limitations of DSM-5, including cultural and ethical considerations. | 1.0 |
| rub_psychology_0003 | Discuss how classical conditioning principles can be applied in modern therapeutic practices. Include examples such as systematic desensitization, aversion therapy, or treatment of phobias. Support discussion with references to key psychological studies and behaviorist theory. | 1.0 |
| rub_psychology_0004 | Evaluate how memory is reconstructed and how this affects the reliability of eyewitness testimony. Refer to cognitive theories and experimental studies (e.g., Loftus & Palmer). Consider implications for the legal system with real or hypothetical examples. | 1.0 |
| rub_psychology_0005 | Explore the psychological and physiological effects of chronic stress. Discuss the role of the HPA axis, impact on immune functioning, and how prolonged stress contributes to mental and physical health conditions. Provide examples and cite supporting research. | 1.0 |
| rub_psychology_0006 | Analyze the role of observational learning in shaping human behavior. Refer to Bandura's Social Learning Theory, including modelling, vicarious reinforcement, and self-efficacy. Provide real-life examples and discuss implications for education or media. | 1.0 |
| rub_psychology_0007 | Short answer: What is the difference between trait and state anxiety? Provide examples and explain how each is measured in psychological research. | 1.0 |
| rub_psychology_0008 | Describe the key features of Piaget's theory of cognitive development. Choose one stage and explain how it manifests in real-world child behavior. Use examples and relate to educational or parenting practices. | 1.0 |
| rub_psychology_0009 | Short answer: What is the fundamental attribution error? Describe a real-life situation where someone might commit this error, and briefly explain its significance in social psychology. | 1.0 |
| rub_psychology_0010 | In 400-600 words, explain how stereotypes influence how people perceive and judge others. Discuss psychological processes (e.g., schema theory, implicit bias, confirmation bias) and provide real-world or hypothetical examples. Essay must follow academic structure with APA references. | 1.0 |
| rub_psychology_0011 | Evaluate the theory of cognitive dissonance and its impact on individual decision-making and behavior modification. Use real-world examples to support your analysis. | 1.0 |
| rub_psychology_0012 | Critically evaluate Maslow's Hierarchy of Needs and its relevance to modern motivation research and workplace psychology. | 1.0 |
| rub_psychology_0013 | Analyze the Big Five personality traits (OCEAN) and evaluate their predictive validity for life outcomes such as academic success, job performance, health, and relationships. | 1.0 |
| rub_psychology_0014 | Critically discuss classical and operant conditioning, comparing their mechanisms, key experiments, and applications in behavior change (e.g., phobias, habit formation, education). | 1.0 |
| rub_psychology_0015 | Evaluate cognitive-behavioral therapy (CBT) as an evidence-based treatment for depression and anxiety, considering mechanisms of change, efficacy, and limitations. | 1.0 |
| rub_psychology_0016 | Discuss the role of working memory in complex cognition, evaluating models (e.g., Baddeley-Hitch) and links to reasoning, language, and learning. | 1.0 |
| rub_psychology_0017 | Examine attachment theory from infancy to adulthood, comparing attachment styles, measurement methods, and implications for relationships and mental health. | 1.0 |
| rub_psychology_0018 | Critically evaluate the biopsychosocial model of health and illness, including its advantages over reductionist models and challenges in clinical implementation. | 1.0 |
| rub_psychology_0019 | Assess social identity theory and its applications to intergroup relations, prejudice, and organizational behavior. | 1.0 |
| rub_psychology_0020 | Analyze decision-making under uncertainty through the lens of heuristics and biases, comparing with prospect theory and dual-process models. | 1.0 |

### Teaching

| Rubric ID | Prompt | Schema Version |
|-----------|--------|----------------|
| rub_teaching_0001 | Active Learning Strategies: Evaluate the impact of active learning strategies on student engagement and academic success in higher education. Provide evidence-backed recommendations for instructors looking to maximize participation and outcomes through active learning. | 1.0 |
| rub_teaching_0002 | Challenges in Online Education: Evaluate the challenges and opportunities of online education in higher education, and analyze effective strategies for student engagement and instructional quality in virtual learning environments. | 1.0 |
| rub_teaching_0003 | Critical Thinking Skills Development: Discuss the development of critical thinking skills in tertiary education and propose methods to cultivate analytical reasoning among students. | 1.0 |
| rub_teaching_0004 | Collaborative Learning Strategies: Analyze the effectiveness of collaborative learning strategies and their impact on group dynamics and knowledge construction. | 1.0 |
| rub_teaching_0005 | Assessment Strategies in K-12 Settings: Discuss various assessment strategies suitable for K-12 education and their influence on personalized learning. | 1.0 |
| rub_teaching_0006 | Formative vs Summative Assessment: Analyze the roles of formative and summative assessment in supporting student achievement, and discuss best practices for using assessment data to guide instructional decisions. | 1.0 |
| rub_teaching_0007 | Inclusive Education for Diverse Learners: Evaluate the principles and practices of inclusive education and their effects on learner outcomes and equity. | 1.0 |
| rub_teaching_0008 | Education Policy Analysis: Critically analyze current education policies and their effects on school performance and equity. | 1.0 |
| rub_teaching_0009 | Educational Leadership and Change: Discuss the role of educational leadership in driving change and fostering innovation within schools. | 1.0 |
| rub_teaching_0010 | Literacy Development in Early Grades: Examine approaches to early grade literacy development and their impact on student academic trajectories. | 1.0 |
| rub_teaching_0011 | Student-Centered Learning Approaches: Evaluate student-centered learning approaches and analyze their effects on engagement, motivation, and academic success. | 1.0 |
| rub_teaching_0012 | Integration of Educational Technology: Discuss how the integration of educational technology can enhance teaching and learning, and analyze best practices for effective implementation in classrooms. | 1.0 |
| rub_teaching_0013 | Multicultural Education Practices: Explore multicultural education practices and their role in promoting cultural competence and inclusion in classrooms. | 1.0 |
| rub_teaching_0014 | Ethics in Educational Assessment: Analyze ethical considerations in educational assessment and discuss frameworks for maintaining fairness and integrity. | 1.0 |
| rub_teaching_0015 | Global Competence Development: Discuss the development of global competence in students and strategies for integrating global perspectives into curricula. | 1.0 |
| rub_teaching_0016 | Discuss how play-based learning supports the cognitive, social, and emotional development of children in early childhood settings. | 1.0 |
| rub_teaching_0017 | Analyse the role of attachment theory in early childhood education and how educators can create secure learning environments. | 1.0 |
| rub_teaching_0018 | Compare different developmental theories (Piaget, Vygotsky, Montessori) and evaluate their practical applications in early childhood programs. | 1.0 |
| rub_teaching_0019 | Examine how socioeconomic factors might impact early childhood development and propose strategies to support children from diverse economic backgrounds. | 1.0 |
| rub_teaching_0020 | Evaluate the benefits and challenges of technology integration in early childhood education for children aged 3 to 6 years. | 1.0 |
| rub_teaching_0021 | Discuss culturally and linguistically responsive practices for children from non-English speaking backgrounds and analyse how to create inclusive environments that support both home languages and English development. | 1.0 |
| rub_teaching_0022 | Analyse the transition process from home to early childhood programs and discuss strategies for supporting children and families during this critical period. | 1.0 |
| rub_teaching_0023 | Analyse the role of family engagement in early childhood education and develop a plan for building meaningful educator-family partnerships. | 1.0 |
| rub_teaching_0024 | Investigate the significance of outdoor education and nature-based learning in early childhood development, including benefits and implementation considerations. | 1.0 |
| rub_teaching_0025 | Examine current research on early literacy development and evaluate evidence-based approaches for supporting pre-reading skills in diverse learners aged 3 to 6 years. | 1.0 |

### Accounting

| Rubric ID | Prompt | Schema Version |
|-----------|--------|----------------|
| rub_accounting_0001 | Analyze the impact of blockchain technology on traditional accounting practices, including auditing and financial reporting. | 0.5 |
| rub_accounting_0002 | Discuss the ethical considerations for accountants in the age of big data and artificial intelligence. | 0.5 |
| rub_accounting_0003 | Evaluate the role of forensic accounting in detecting and preventing financial fraud in digital environments. | 0.5 |
| rub_accounting_0004 | Analyze the implications of environmental, social, and governance (ESG) reporting on corporate financial transparency and investor decision-making. | 0.5 |
| rub_accounting_0005 | Examine the challenges and opportunities for small and medium-sized enterprises (SMEs) in adopting cloud-based accounting software. | 0.5 |
| rub_accounting_0006 | Discuss the impact of robotic process automation (RPA) on the efficiency and accuracy of financial operations within large corporations. | 0.5 |
| rub_accounting_0007 | Analyse the accounting and auditing implications of cryptocurrencies and digital assets for businesses. | 0.5 |
| rub_accounting_0008 | Discuss the increasing importance of data analytics in modern auditing and its impact on audit quality and efficiency. | 0.5 |
| rub_accounting_0009 | Evaluate the current state and future prospects of integrated reporting, focusing on its benefits for stakeholders and challenges in implementation. | 0.5 |
| rub_accounting_0010 | Analyze the impact of global tax reforms, such as the OECD's Pillar One and Pillar Two initiatives, on multinational corporations' tax strategies and financial reporting. | 0.5 |
| rub_accounting_0011 | Evaluate the impact of ethical standards on financial reporting and the consequences of ethical breaches in accounting practices. | 1.0 |
| rub_accounting_0012 | Discuss how the adoption of IFRS influences financial transparency and comparability for multinational companies. | 1.0 |
| rub_accounting_0013 | Evaluate how managerial accounting contributes to internal decision-making and organizational strategy. | 1.0 |
| rub_accounting_0014 | Compare the advantages and drawbacks of fair value and historical cost accounting in financial reporting. | 1.0 |
| rub_accounting_0015 | Evaluate how ethical principles support auditor independence and prevent conflicts of interest in financial audits. | 1.0 |
| rub_accounting_0016 | Analyze the role of environmental, social, and governance (ESG) reporting in enhancing accountability and long-term corporate performance. | 1.0 |
| rub_accounting_0017 | Evaluate how forensic accounting techniques support fraud detection and legal proceedings. | 1.0 |
| rub_accounting_0018 | Analyze how digital technologies such as AI, blockchain, and cloud computing are transforming accounting workflows and controls. | 1.0 |
| rub_accounting_0019 | Evaluate how different taxation strategies and regulations influence a corporation's financial decision-making. | 1.0 |
| rub_accounting_0020 | Discuss how effective internal control systems reduce the risk of fraud and support compliance in organizations. | 1.0 |

### IT

| Rubric ID | Prompt | Schema Version |
|-----------|--------|----------------|
| rub_it_0001 | Critically evaluate zero-trust architecture in enterprise security. Discuss its core principles, benefits, and challenges in implementation. Provide examples of how zero-trust improves security posture compared to traditional perimeter-based models, and analyze potential limitations. | 0.5 |
| rub_it_0002 | Evaluate the effectiveness of multi-factor authentication (MFA) in preventing data breaches. Discuss various MFA methods, their usability and security trade-offs, and how MFA integrates into broader cybersecurity strategies. | 0.5 |
| rub_it_0003 | Analyze social engineering attacks and human vulnerabilities in cybersecurity. Explore common types of social engineering, psychological principles exploited, and measures to enhance human resilience. | 0.5 |
| rub_it_0004 | Evaluate the impact of ransomware attacks on critical infrastructure. Discuss attack vectors, consequences for essential services, and strategies for prevention and recovery. | 0.5 |
| rub_it_0005 | Discuss the role of cybersecurity audits in compliance and risk management. Evaluate how audits help organizations identify vulnerabilities, ensure regulatory adherence, and support continuous security improvement. | 0.5 |
| rub_it_0006 | Analyze the impact of 5G technology on IoT scalability and speed. Discuss benefits and challenges 5G brings to loT devices and networks, including security implications. | 0.5 |
| rub_it_0007 | IPv6 adoption: Why is the transition still slow? Discuss technical, operational, and organizational challenges delaying IPv6 uptake despite its advantages. | 0.5 |
| rub_it_0008 | Compare software-defined networking (SDN) with traditional networking. Evaluate their architectures, benefits, and limitations in modern IT infrastructure. | 0.5 |
| rub_it_0009 | Discuss the role of edge computing in latency-sensitive applications. Explain how edge computing improves performance and security compared to centralized cloud models. | 0.5 |
| rub_it_0010 | Explain how DNS over HTTPS (DOH) enhances user privacy. Discuss its technical mechanisms, benefits, and potential challenges in adoption. | 0.5 |
| rub_it_0021 | Discuss the advantages of NoSQL databases in modern web applications. | 0.5 |
| rub_it_0022 | How does data warehousing support business intelligence? | 0.5 |
| rub_it_0023 | Explain the role of data normalization in relational database design. | 0.5 |
| rub_it_0024 | Evaluate database backup strategies for disaster recovery. | 0.5 |
| rub_it_0025 | Discuss the ethical challenges in big data collection and analysis. | 0.5 |
| rub_it_0026 | Agile vs. Waterfall methodologies: Which suits modern development better? | 0.5 |
| rub_it_0027 | Explain how continuous integration improves software quality. | 0.5 |
| rub_it_0028 | Explain the importance of test-driven development (TDD) in large codebases. | 0.5 |
| rub_it_0029 | Discuss strategies for managing technical debt in long-term software projects. | 0.5 |
| rub_it_0030 | Explain the role of containerization (e.g., Docker) in CI/CD pipelines. | 0.5 |

### Engineering

| Rubric ID | Prompt | Schema Version |
|-----------|--------|----------------|
| rub_engineering_0001 | How a mechanical engineer analyzes stress in a loaded beam-problem definition, assumptions, equations, techniques, and reporting. | 0.5 |
| rub_engineering_0002 | Full process for a simple resistive circuit: identify outputs, select components, perform calculations, draw schematics, validate against specs. | 0.5 |
| rub_engineering_0003 | Logical approach to plan a pedestrian bridge-site analysis, assumptions, structure, materials, load capacity, and presentation. | 0.5 |
| rub_engineering_0004 | Define the problem, select treatment process(es), and present findings for municipal water contamination. | 0.5 |
| rub_engineering_0005 | Step-by-step design of a batch reactor: problem structure, equations/kinetics, and design justification. | 0.5 |
| rub_engineering_0006 | Improve hybrid fuel efficiency using simulations, constraints, energy-flow calculations, and stakeholder reporting. | 0.5 |
| rub_engineering_0007 | Analytical approach to design a mid-rise in earthquake zones-loads, equations, safety margins, documentation. | 0.5 |
| rub_engineering_0008 | Determine satellite trajectory-orbital principles, conceptual choices, assumptions, and validation/visualization. | 0.5 |
| rub_engineering_0009 | Decompose complex requirements, design architecture, test modules, and document the process. | 0.5 |
| rub_engineering_0010 | Define delays, collect data, model the process, and propose improvements. | 0.5 |
| rub_engineering_0011 | Describe how a manufacturing engineer sets up a basic production line for a new consumer product. Explain the steps taken from design to assembly, including equipment layout, efficiency considerations, and safety. | 0.5 |
| rub_engineering_0012 | How would you design a basic cooling system (e.g., for a computer or small motor)? Discuss how heat transfer principles are applied, what materials might be used, and how airflow is managed. | 0.5 |
| rub_engineering_0013 | Explain how an environmental engineer would create a waste management plan for a small town. Include types of waste, collection methods, environmental impact, and basic solutions like recycling or composting. | 0.5 |
| rub_engineering_0014 | Describe the key steps and safety considerations involved in planning and installing a simple home electrical wiring system. Focus on circuit breakers, outlet placement, and energy consumption. | 0.5 |
| rub_engineering_0015 | Explain the basic process of soap production using chemical engineering principles. Discuss the raw materials, reactions involved, and how the final product is tested for quality. | 0.5 |
| rub_engineering_0016 | A section of a road is damaged. Explain how a civil engineer would assess the damage, plan the repair, and ensure long-term durability of the fix, considering weather and usage. | 0.5 |
| rub_engineering_0017 | Describe how a computer engineer would design a simple smart home system to control lights and appliances. Include sensors, communication methods (like Wi-Fi), and user interface ideas. | 0.5 |
| rub_engineering_0018 | How would a construction engineer plan and execute the building of a small emergency shelter? Discuss site preparation, material choice, basic structure design, and time management. | 0.5 |
| rub_engineering_0019 | Discuss how a transportation engineer could improve the design and placement of public bus stops in a busy city. Mention factors like accessibility, safety, and weather protection. | 0.5 |
| rub_engineering_0020 | Describe how a biomedical engineer would approach designing a simple assistive device (e.g., a low-cost walking aid). Consider the user's needs, materials, and testing for usability. | 0.5 |