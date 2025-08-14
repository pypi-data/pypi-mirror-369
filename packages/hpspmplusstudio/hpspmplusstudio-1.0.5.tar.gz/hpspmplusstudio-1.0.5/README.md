**hpSPM+ Studio Library Description**

The **hpSPM+ Studio Python Library** is a powerful API designed for seamless interaction with **hpSPM+ systems**, providing comprehensive tools for system customization, real-time monitoring, and data management. Its modular structure allows easy integration into scientific and industrial workflows.

Key features include:

- **Device Control**:
  - Complete control over scanning processes, voltage configurations, and offset adjustments.
  - Optimizes system performance with automatic calibration and setup features.
- **Real-Time System Monitoring**:
  - Provides real-time access to essential metrics like system status and scan progress.
  - Delivers detailed feedback on scanning status, voltage levels, and system activities.
- **Data Management**:
  - Records, organizes, and analyzes scanned images and system readings.
  - Offers the ability to manage image containers effectively.
- **Customizable Solutions**:
  - Configures scanning parameters and other settings to meet experimental or industrial requirements.
  - Its modular design enhances system scalability.

This library is an ideal tool for automating workflows, optimizing device performance, and developing custom applications.

# Prerequisites

- **Operating System:** Windows 10 or later.
- **Python Version:** Python versions 3.9 to 3.12. Download Python from python.org.
- **hpSPM+ Studio Software:** The hpSPM+ Studio software must be installed, and its API feature should be activated.
- **Network Access:** The hpSPM+ device must be accessible via its designated IP address and port.
- **pip Package Manager:** The Python pip package manager is required to install the library.
- **Dependencies:** All required dependencies are installed automatically during the library setup.
- **Development Environment (Recommended):** Using Visual Studio Code is recommended for writing, debugging, and running Python scripts.

**Note:** Ensure your Python environment is properly configured before proceeding with the installation.

# Installation and Upgrading

- **To Install the hpSPM+ Python Library:**
  - Open a Windows Command Prompt or terminal with Python installed.
  - Enter the following command:

pip install hpspmplusstudio

- **To Upgrade to the Latest Version of the hpSPM+ Library:**
  - Use the following command:

pip install hpspmplusstudio -U

**Note:** Ensure your Python environment meets all the prerequisites listed before proceeding with the installation or upgrade.

# Running the Examples

The **hpSPM+ Studio Python Library** provides comprehensive documentation, sample scripts, and application templates to help users get started quickly. These resources are organized into separate directories such as Docs and Samples within the package.

To locate these files on your system, follow these steps:

1. Open a terminal or command prompt with Python installed.
2. Enter the following commands to access the library's help feature:

python

\>>> import hpSPMPlusStudio

\>>> hpSPMPlusStudio.help()

1. The output will display the exact paths to the documentation (Docs) and example scripts (Samples). For instance:
    1. **Docs**: Contains the PDF manual and library overview files.
    2. **Samples**: Includes subfolders like Basics and Experiments with practical examples.

We recommend using **Visual Studio Code** or a similar IDE for writing, debugging, and running Python scripts. You can explore the examples in the Samples folder to better understand how to interact with the hpSPM+ API and customize it for your needs.