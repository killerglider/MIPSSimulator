from prettytable import prettytable

class MIPSPipelineSimulator:
    def __init__(self, instructions):
        self.instructions = instructions
        self.pipeline = [None] * 5  # Representing IF, ID, EX, MEM, WB
        self.clock_cycle = 0
        self.registers = {f'$r{i}': 0 for i in range(32)}  # 32 General-purpose registers
        self.memory = {}  # Simple memory model
        self.pipeline_history = []  # For storing pipeline state

    def fetch(self, pc):
        if pc < len(self.instructions):
            return self.instructions[pc]
        return None

    def decode(self, instruction):
        if instruction is None:
            return None
        parts = instruction.split()
        op = parts[0]
        args = parts[1].split(',')
        return op, [arg.strip() for arg in args]

    def execute(self, op, args):
        if op == 'ADD':
            rd, rs, rt = args
            self.registers[rd] = self.registers[rs] + self.registers[rt]
        elif op == 'SUB':
            rd, rs, rt = args
            self.registers[rd] = self.registers[rs] - self.registers[rt]
        elif op == 'LW':
            rt, offset_base = args
            offset, base = offset_base.split('(')
            base = base[:-1]  # Remove closing parenthesis
            self.registers[rt] = self.memory.get(self.registers[base] + int(offset), 0)
        elif op == 'SW':
            rt, offset_base = args
            offset, base = offset_base.split('(')
            base = base[:-1]  # Remove closing parenthesis
            self.memory[self.registers[base] + int(offset)] = self.registers[rt]

    def write_back(self, op, args):
        # For simplicity, write-back logic is merged with execute
        pass

    def run(self):
        pc = 0
        while any(stage is not None for stage in self.pipeline) or pc < len(self.instructions):
            self.clock_cycle += 1
            print(f'Clock Cycle {self.clock_cycle}:')

            # Write Backstage
            if self.pipeline[4]:
                op, args = self.pipeline[4]
                self.write_back(op, args)
                print(f'  WB: {self.pipeline[4]}')
                self.pipeline[4] = None

            # Memory Access stage
            if self.pipeline[3]:
                print(f'  MEM: {self.pipeline[3]}')
                self.pipeline[4] = self.pipeline[3]
                self.pipeline[3] = None

            # Execute stage
            if self.pipeline[2]:
                op, args = self.pipeline[2]
                self.execute(op, args)
                print(f'  EX: {self.pipeline[2]}')
                self.pipeline[3] = self.pipeline[2]
                self.pipeline[2] = None

            # Instruction Decode stage
            if self.pipeline[1]:
                op, args = self.decode(self.pipeline[1])
                print(f'  ID: {self.pipeline[1]}')
                self.pipeline[2] = (op, args)
                self.pipeline[1] = None

            # Instruction Fetch stage
            if pc < len(self.instructions):
                instruction = self.fetch(pc)
                print(f'  IF: {instruction}')
                self.pipeline[1] = instruction
                pc += 1

            # Save pipeline state for visualization
            self.pipeline_history.append(self.pipeline.copy())

            print(f'Registers: {self.registers}')
            print(f'Memory: {self.memory}')
            print('-' * 50)

        self.display_pipeline_chart()

    def display_pipeline_chart(self):
        table = prettytable()
        table.field_names = ["Clock Cycle", "IF", "ID", "EX", "MEM", "WB"]

        for cycle, state in enumerate(self.pipeline_history, start=1):
            table.add_row([
                cycle,
                state[0] if state[0] else "",
                state[1] if state[1] else "",
                state[2] if state[2] else "",
                state[3] if state[3] else "",
                state[4] if state[4] else ""
            ])

        print("Pipeline Execution Chart:")
        print(table)

# Example program
instructions = [
    'LW $r1, 0($r0)',
    'LW $r2, 4($r0)',
    'ADD $r3, $r1, $r2',
    'SW $r3, 8($r0)'
]

simulator = MIPSPipelineSimulator(instructions)
simulator.run()
