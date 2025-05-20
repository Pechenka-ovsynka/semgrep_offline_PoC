const { exec } = require('child_process');

class DockerCompose {
  constructor(dockerComposeFilePath, enableLog = false) {
    this.dockerComposeFilePath = dockerComposeFilePath;
    this.enableLog = enableLog;
  }

  async down() {
    return this.execComposeCommand('down --remove-orphans');
  }

  async upAll() {
    return this.execComposeCommand('up -d');
  }

  async getExternalPort(serviceName, internalPort) {
    const portCommandOutput = await this.execComposeCommand(`port ${serviceName} ${internalPort}`);
    const externalPort = (portCommandOutput.split(':')[1]).replace('\n', '');
    return externalPort;
  }

  execComposeCommand(command) {
    return new Promise((resolve, reject) => {
      const composeCommand = `docker-compose -f ${this.dockerComposeFilePath} ${command}`;
      // DEEP: command is tainted by `userInput` at line 38
      exec(composeCommand, (error, stdout, stderr) => {
        if (this.enableLog) { console.log({ error, stdout, stderr }); }
        if (error) { reject(error); } else { resolve(stdout); }
      });
    });
  }
};


function main() {
  const dc = new DockerCompose('razdva');
  dc.execComposeCommand(userInput());
}
