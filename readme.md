<center><h1>RL 1v1 Tower Logic</h1></center>

# Overview
This repository serves to house the underlying logic for the [Rocket League 1v1 Tower Bot](https://github.com/rrenode/1v1-Tower-Discord-Bot) (a cool name would be nice). The tower logic is built here, tested, and then implemented into the Discord Bot. Currently development is for the [GrindHouse Discord Server](https://discord.gg/grindhouse)'s 1v1 tower, though discussions about expanding the bot and logic to an API both for other developers and players alike have been considered.

# Contributing
### How to Contribute
1. **Fork the Repository** 
	- Navigate to the project's GitHub page and click the "Fork" button at the top right to create your own copy of the repository. 
2. **Clone the Repository** 
	- Clone your forked repository to your local machine: ```sh git clone https://github.com/rrenode/1v1-Tower-Logic.git ``` 
	- Navigate into the cloned directory: ```sh cd 1v1-Tower-Logic ```
3.  **Create a Branch** 
	- Create a new branch for your changes:
		- For features: ```sh git checkout -b feature/feature-name ``` 
		- For bug fixes: ```sh git checkout -b bugfix/bug-fix-name ``` 
4. **Install requirements**
	- **IMPORTANT:** As of now, the repository does not have any requirements. 
	- In CLI: ```py -m pip install -r "requirements.txt"```
5. **Make Your Changes** 
	- Implement your changes in the new branch.
	- Follow the coding standards and guidelines of the project.
	- Make sure to update or add tests as appropriate. 
6. **Commit Your Changes** 
	- Commit your changes with a meaningful commit message: ```sh git add . git commit -m "Description of the changes you made" ``` 
7. **Push Your Changes** 
	- Push the changes to your forked repository:
		- For features: ```sh git push origin feature/feature-name```
		- For bug fixes:: ```she git push origin bugfix/bug-fix-name```
8. **Open a Pull Request** 
	- Go to the original repository and click on "New Pull Request". 
	- Select the branch you just pushed to and submit your pull request. 
	- Provide a detailed description of your changes in the pull request.

### Contribution Guidelines
- **Code Style**: Follow the existing code style in the project. Consistency is key to maintainability. 
- **Testing**: Ensure that your code passes all tests and that you add tests for new features or bug fixes. 
- **Documentation**: Update documentation to reflect your changes, if applicable. 
- **Commits**: Write clear, concise commit messages that explain the "what" and "why" of your changes.

### Reporting Issues 
If you find a bug or have a feature request, please open an issue on GitHub. Include as much detail as possible to help us understand and address the issue. 
1. **Check Existing Issues**: Before opening a new issue, check if the issue already exists. 
2. **Create a New Issue**: If the issue doesn’t exist, open a new issue and provide the following information: 
	- A descriptive title
	- Detailed description of the issue
	- Steps to reproduce the issue
	- Any relevant logs, screenshots, or other information

## Running Tests
Testing has been implemented with unittest and unittest.mock from the Python standard libraries. The tests are stored in the directory [1v1-Tower-Logic/tests](https://github.com/rrenode/1v1-Tower-Logic/tree/develop/tests). Substantional work is needed before these tests begin proving useful, but alas the foundation is laid for their use.
