import express from 'express';
import { authenticate, AuthRequest } from '../middleware/auth';
import prisma from '../config/database';
import { createTaskSchema } from '../utils/validation';
import { AppError } from '../middleware/errorHandler';

const router = express.Router();

router.use(authenticate);

router.get('/', async (req: AuthRequest, res, next) => {
  try {
    const { projectId, status, assigneeId } = req.query;

    const where: any = {
      project: {
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id } } },
        ],
      },
    };

    if (projectId) where.projectId = projectId;
    if (status) where.status = status;
    if (assigneeId) where.assigneeId = assigneeId;

    const tasks = await prisma.task.findMany({
      where,
      include: {
        project: {
          select: { id: true, name: true, color: true },
        },
        assignee: {
          select: { id: true, name: true, email: true, avatar: true },
        },
        _count: {
          select: { comments: true, attachments: true },
        },
      },
      orderBy: { createdAt: 'desc' },
    });

    res.json(tasks);
  } catch (error) {
    next(error);
  }
});

router.get('/:id', async (req: AuthRequest, res, next) => {
  try {
    const task = await prisma.task.findFirst({
      where: {
        id: req.params.id,
        project: {
          OR: [
            { ownerId: req.user!.id },
            { members: { some: { userId: req.user!.id } } },
          ],
        },
      },
      include: {
        project: {
          select: { id: true, name: true, color: true },
        },
        assignee: {
          select: { id: true, name: true, email: true, avatar: true },
        },
        comments: {
          include: {
            user: {
              select: { id: true, name: true, email: true, avatar: true },
            },
          },
          orderBy: { createdAt: 'asc' },
        },
        attachments: {
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    if (!task) {
      throw new AppError('Task not found', 404);
    }

    res.json(task);
  } catch (error) {
    next(error);
  }
});

router.post('/', async (req: AuthRequest, res, next) => {
  try {
    const validatedData = createTaskSchema.parse(req.body);

    // Verify user has access to project
    const project = await prisma.project.findFirst({
      where: {
        id: validatedData.projectId,
        OR: [
          { ownerId: req.user!.id },
          { members: { some: { userId: req.user!.id } } },
        ],
      },
    });

    if (!project) {
      throw new AppError('Project not found or insufficient permissions', 404);
    }

    const task = await prisma.task.create({
      data: {
        title: validatedData.title,
        description: validatedData.description,
        status: validatedData.status || 'todo',
        priority: validatedData.priority || 'medium',
        dueDate: validatedData.dueDate ? new Date(validatedData.dueDate) : null,
        projectId: project.id,
        assigneeId: validatedData.assigneeId,
      },
      include: {
        project: {
          select: { id: true, name: true, color: true },
        },
        assignee: {
          select: { id: true, name: true, email: true, avatar: true },
        },
      },
    });

    res.status(201).json(task);
  } catch (error) {
    next(error);
  }
});

router.put('/:id', async (req: AuthRequest, res, next) => {
  try {
    const task = await prisma.task.findFirst({
      where: {
        id: req.params.id,
        project: {
          OR: [
            { ownerId: req.user!.id },
            { members: { some: { userId: req.user!.id } } },
          ],
        },
      },
    });

    if (!task) {
      throw new AppError('Task not found', 404);
    }

    const validatedData = createTaskSchema.partial().parse(req.body);

    const updatedTask = await prisma.task.update({
      where: { id: req.params.id },
      data: {
        ...validatedData,
        dueDate: validatedData.dueDate ? new Date(validatedData.dueDate) : undefined,
      },
      include: {
        project: {
          select: { id: true, name: true, color: true },
        },
        assignee: {
          select: { id: true, name: true, email: true, avatar: true },
        },
      },
    });

    res.json(updatedTask);
  } catch (error) {
    next(error);
  }
});

router.delete('/:id', async (req: AuthRequest, res, next) => {
  try {
    const task = await prisma.task.findFirst({
      where: {
        id: req.params.id,
        project: {
          OR: [
            { ownerId: req.user!.id },
            { members: { some: { userId: req.user!.id, role: { in: ['owner', 'admin'] } } } },
          ],
        },
      },
    });

    if (!task) {
      throw new AppError('Task not found or insufficient permissions', 404);
    }

    await prisma.task.delete({
      where: { id: req.params.id },
    });

    res.json({ message: 'Task deleted successfully' });
  } catch (error) {
    next(error);
  }
});

export default router;
