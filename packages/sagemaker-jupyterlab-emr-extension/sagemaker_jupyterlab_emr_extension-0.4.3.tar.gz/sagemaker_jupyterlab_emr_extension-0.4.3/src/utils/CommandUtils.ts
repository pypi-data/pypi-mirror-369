import { CommandRegistry } from '@lumino/commands';
import { ReadonlyPartialJSONObject } from '@lumino/coreutils';
import { COMMAND_IDS } from '../constants/common';

/**
 * Defines a Command
 */
type Command = (data: object | undefined) => void;
/**
 * Defines a wrapper of a registry to a Command
 */
type CommandRegistryWrapper = (registry: CommandRegistry) => Command;

interface SageMakerCommand {
  readonly id: COMMAND_IDS;
  readonly createRegistryWrapper: CommandRegistryWrapper;
  readonly execute: (registry: CommandRegistry, data: object | undefined) => void;
}

/**
 * Defines a Map of Command functions
 */
type CommandsMap = { [key in keyof typeof COMMAND_IDS]?: Command };
type SageMakerJupyterLabEmrCommandMap = { [key in keyof typeof COMMAND_IDS]: SageMakerCommand };

const executeCommand = (command: COMMAND_IDS, registry: CommandRegistry, data: object | undefined) => {
  registry.execute(command, data as ReadonlyPartialJSONObject);
};

/**
 * Creates a closure around a JP phosphor command constant
 * so it can be executed inside a deeply nested component
 * without direct awareness of JupyterLabs
 * @return another function which will close around the registry object in a widget
 */
const wrapRegistryCommand = (command: COMMAND_IDS) => (registry: CommandRegistry) => (data: object | undefined) => {
  executeCommand(command, registry, data);
};

const createCommand = (command: COMMAND_IDS): SageMakerCommand => ({
  id: command,
  createRegistryWrapper: wrapRegistryCommand(command),
  execute: (registry: CommandRegistry, data: object | undefined) => executeCommand(command, registry, data),
});

/**
 * Create commands for export here:
 */
const COMMANDS: SageMakerJupyterLabEmrCommandMap = Object.fromEntries(
  Object.entries(COMMAND_IDS).map((entry) => {
    const key = entry[0];
    const value = entry[1];
    return [key, createCommand(value)];
  }),
) as SageMakerJupyterLabEmrCommandMap;

export { COMMANDS, Command, CommandsMap };
