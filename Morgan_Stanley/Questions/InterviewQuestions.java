// MORGAN STANLEY INTERVIEW QUESTIONS
// Compiled from interview preparation materials

/*
================================================================================
GENERAL INTERVIEW QUESTIONS
================================================================================

Question:
What do you look for when you review someone else's code for vulnerabilities? 
What areas of things you'd consider that you can use in previous work, if any? 
Provide few examples.

How do you design different type of testing? 
What type of testing do you perform before delivering the code to CA?

Architecture:
- Different type of annotations and their uses & characteristics. 
Exceptions architect (10&4+) in sections architect.xml
- How to framework vs library (short framework) have you used? 
How is REST the expressed with controller.xml and / data / User's annotation - library - 
something that uses part of framework - something that takes part

- Spring framework - provide examples; what are the most important attributes for good enterprise level solution?
- Formant vs Harness (multi)

General:
- How does Facebook work? How do online meetings get prioritized?
- What do you know about Code architecture, and the risks of focusing data is faster than the user can pay, how would you handle that situation?

Non Technical:
General:
- Reason for leaving current perm What are you know about previous jobs?
- Passion for what you biggest center achievement from your resume?
- Give me a time you had to take position under pressure.
- Areas of Improvement? What are you doing about it?
- What if you were hired about One recent learning? Any favorite blog, Innovation, magazine, etc?

Financial:
- Work on Change in future
- Most popular stock market makers and differences

Planning/Time Management:
- Agile vs Waterfall - what's the difference?
- How much planning vs. pre-testing you do before you deploy?
- How much difference planning can you make you might miss deadline?

Managerial:
- How did you define your management style?
- How do you balance the needs of the business vs incredible while staying?
- How will you handle short temper and reactive employee who is very good technically?

Interactive Exercises:
1. Coding
   - Write what you prefer an O(nlogn) vs flow the best non-recursive character is a string. What new structure did they use? What was congratulating concerns
   - How can we write faster? Can you write all string in parallel with a paragraph of the statement is a string
   - Favorite expression for array exercises
   - How do you know if a string is an anagram? For example, can the string "programming" be rearranged to "grammingpro"? (message) Write about H how to is a big List H8 and then whether to compute it
   - Can take the even numbers from the code

2. What is...
   - Given a java or C# class of a Student, show me a code you will create you shall have student this, where you are going to create it. (i.e. if that student uses unique) you are and you how it
   How should you do? For you can make if code If it involve you how and how you have to make to sure that it was for and how the
   - Code can use a course a choose the issue is so as we and choose as make use and how you
   - How do you know what you can be that able to that i can - can that you get a table the where you go class code
   - How can we do i create any Suppose some code cannot code how some unique

================================================================================
SPRING FRAMEWORK QUESTIONS
================================================================================

Spring Questions:
• How do you build spring boot
  ○ expectation: maven, gradle
  ○ maven questions: failure to answer not acceptable
    ▪ What is the config file for maven?
    ▪ expectation: pom.xml (non answer), settings.xml (extra points)
  ○ maven.id group id, artifact id, packaging type
    ▪ expectation: default package type is "jar"
  ○ What is the dependency for a springboot app in pom.xml?
    ▪ expectation: spring-boot-starter-web

• What are maven goals?
  ○ expectation: at least should know package, install
  ○ expectation: spring boot is a jar file

• What is the output of the build?
  ○ expectation: spring boot is a jar file

• What is inside the jar?
  ○ expectation: spring mvc is a xml file

• What annotation do you use in your app?
  ○ expectation: @RestController, @RequestMapping, @Repository
  ○ Grade questions: failure to answer - acceptable - extra points
    ▪ What are configuration files for gradle?
    ▪ expectation: build.gradle, gradle.properties, settings.gradle

Spring MVC questions:
• What is the DispatcherServlet?
  ○ expectation: maven, gradle
  ○ Build maven/gradle question
    ▪ What is the config file for maven?
    ▪ expectation: pom.xml (non answer), settings.xml (extra points)
  ○ gradle.id group id, artifact id, packaging type
    ▪ expectation: default package type is "jar"
  ○ What is the output of the build?
    ▪ expectation: spring mvc is a xml file
  ○ what is the jar file and the...
  ○ expectation: web xml (and other xml), classes, properties
  ○ Bonus xml is not matched in servlet spec 3.0
  ○ what xml files are there
    ▪ expectation: web.xml, servlet.xml

Senior Dev questions:
Ask the candidate (something like): In your past experience can you describe an enterprise grade java dev project you worked on?
Expectation: they will provide some context

• Answers such as: I don't know about other things, this was my part - is a failure to take interest, ownership
• Answers such as: We were the project / had features here is what the other teams and the project planning and ownership and awareness.

Questions to follow-up (immediately?), otherwise:

1. Functional Design
  a. Code and Design of application
  b. Layering your application
  c. General architecture
  d. Making requirements captured and reviewed by candidate

2. Non functional
  a. Handling errors
  b. Monitoring - before failure causes
  c. Performance
  d. Scalability
  e. Reliability
  f. Security - How do they deal with external Open api

================================================================================
INTERVIEW STEP 3: GENERAL QUESTIONS - 15 mins
================================================================================

Java:
• Describe OOP and its uses there
• Have you you worked from some than one class?
• There is also Three cases in which
• What is Polymorphism? Is it possible with collections?

Build Framework:
• Maven
  ○ What is Maven - something like managing a Maven project
  ○ Basic commands and goals in Maven

Spring:
• What is the concept of Spring? When do you use POJO.JA, beans modeling, JAN, Modules
• What is the default scope of Spring bean?
• What do you prefer about Java dependency and for catching a Spring bean?
• Steps to build the application what for catching a Spring been project be of xml?
• Using a in a process and not support from a Spring been project at of xml?

Self starter related:
• Were are you learning?
  ○ Is learning you are that their contemporary (assume a how when you recognized that you years willing to mean outside applying. What did you do about it?
  ○ What specific skills have you gained your process might more is a good sense?

• What makes you (belief) becoming a problematically or responsibility?
  ○ This you are good? and you are problem you go please do it please?
  ○ How you come from a course you some interest in you in please
  ○ What would you do (belief) a course your interest in your please do yes yes

Business Acumen:
• Why did a time you needed to get information from someone who was not very responsive. what did you do?
  ○ How do you stay up informed
  ○ How do you get answers

================================================================================
BUSINESS ACUMEN QUESTIONS
================================================================================

Business Acumen:
• Tell me about a time you needed to get information from someone who was not very responsive. What did you do?
• Give me an example of a time you managed a number of tasks. How did you handle that?
• Give me an example of where you convinced your management on a different approach for a certain issue, than what they instructed to you.
• Tell me about a time where you disagreed with direction you were taking for someone. How did you handle that?
• Tell me about a time where you missed a deadline, what did you do?
• Tell me how you work under pressure.
• How do you balance technical and business and personal?
• How did you stay connected when a job requires you to perform a repetitive task?
• Tell me about time you disagreed with your manager.

================================================================================
SPRING FRAMEWORK EXPERIENCE SCREENING QUESTIONS
================================================================================

Spring framework:
• Spring framework exposure
  ○ Can you tell us your using Framework experience?
  ○ How and Where did you use spring framework?
  ○ Why do you like Spring framework?
  ○ What pain-points did you have from Spring framework?

Hands on:
• Bean management
  ○ What did you do with the spring framework before (creating from project)? adding new bean? adding new method/function? modifying existing config?
  ○ Bean management - whether you have just being using in a new, if you have starting in a spring bean?
    ▪ How did you how spring framework in a place your own bean (in a spring bean)
    ▪ Implement configuring new file - would
    ▪ Expect constructing setup, setter, annotation
  ○ Bean Spring recognize other new beans?
  ○ Set scope of been - it is singleton and/or non-singleton?
    ▪ Manually destroying a been in MVC
  ○ What about dependency been in Spring? Can you explain how it works? How do you include or exclude dependencies?
    ▪ By avoiding been
    ▪ By avoiding classes
    ▪ By avoiding file

• Real-time/construction experience
  ○ How do you create dependency files
  ○ How use real parameters for your own beans
  ○ Real world code then (can this explain in terms of either architecture or design architecture)?
  ○ What would you look at if started to work in Spring? Can you explain how it works? How do you include or exclude components?

• Content Config management
  ○ How do you determine whether a project is XML based or Annotation based?
  ○ What do you determine - what are the XML files, how are the xml file organized?
  ○ Have you worked with multiple properties files?
    ▪ @properties/ file...
  ○ How would you implement such environments?
    ▪ What do you need to tell you such an element class...
  ○ More questions with annotation based
    ▪ How are components you Spring are loaded in xml based? if you Spring-based config?
    ▪ Check @ComponentScan annotation with package scope

================================================================================
SPRING TROUBLESHOOTING
================================================================================

Spring troubleshooting:
• IDE experience
  ○ IDE which you are using for development?
  ○ How can IDE help you in or application context like if isn't available in an application including more a form will dependencies?
  ○ How do you get those - are how do you use IDE?
  ○ Log the auto-allows it. If not showing, enable logging to show all them

• TOOL selection
  ○ If an something in the application could how it can shows INIT_dependencies from other teach to the same company, and do more for party source dependencies. You need to figure out
    ▪ Are IDE related fix it
    ▪ Code analyze
    ▪ JDB support to browse available profile
    ▪ How can ensure check dependency order only
    ▪ How do you deal with this if use long or help it and learn

• Spring Security
  ○ Spring Security experience
    ▪ What experience do you have regarding spring security? (JDA integration)?
  ○ OAUTH mechanism based
    ▪ How do you are used is area it?
    ▪ How do you implement existing filter? How do you hook it up control details?
      • By extending classes
      • By implements classes
      • By Overriding based

• Spring Internal
  ○ Once you logged in, where many using security keep the user details until you present from Thread-pool works?

================================================================================
INTERVIEW STEP 4: QUALIFICATION QUESTIONS - ASSESSMENT
================================================================================

Ex:

Skill                          Topics                                      Comments                    Notes

                              My architecture and share your interested contributions involve
                              some set of work
*/

public class InterviewQuestions {
    // This file serves as a repository of interview questions
    // for Morgan Stanley interview preparation

    // See the comments above for the complete list of questions
    // organized by category
}
