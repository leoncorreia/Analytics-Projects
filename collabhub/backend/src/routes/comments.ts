import express from 'express';
import { authenticate, AuthRequest } from '../middleware/auth';
import prisma from '../config/database';
import { createCommentSchema } from '../utils/validation';
import { AppError } from '../middleware/errorHandler';

const router = express.Router();

router.use(authenticate);

router.post('/', async (req: AuthRequest, res, next) => {
  try {
    const { taskId } = req.body;
    const validatedData = createCommentSchema.parse(req.body);

    // Verify user has access to task's project
    const task = await prisma.task.findFirst({
      where: {
        id: taskId,
        project: {
          OR: [
            { ownerId: req.user!.id },
            { members: { some: { userId: req.user!.id } } },
          ],
        },
      },
    });

    if (!task) {
      throw new AppError('Task not found or insufficient permissions', 404);
    }

    const comment = await prisma.comment.create({
      data: {
        content: validatedData.content,
        taskId,
        userId: req.user!.id,
      },
      include: {
        user: {
          select: { id: true, name: true, email: true, avatar: true },
        },
      },
    });

    res.status(201).json(comment);
  } catch (error) {
    next(error);
  }
});

router.put('/:id', async (req: AuthRequest, res, next) => {
  try {
    const comment = await prisma.comment.findUnique({
      where: { id: req.params.id },
    });

    if (!comment) {
      throw new AppError('Comment not found', 404);
    }

    if (comment.userId !== req.user!.id) {
      throw new AppError('Insufficient permissions', 403);
    }

    const validatedData = createCommentSchema.parse(req.body);

    const updatedComment = await prisma.comment.update({
      where: { id: req.params.id },
      data: validatedData,
      include: {
        user: {
          select: { id: true, name: true, email: true, avatar: true },
        },
      },
    });

    res.json(updatedComment);
  } catch (error) {
    next(error);
  }
});

router.delete('/:id', async (req: AuthRequest, res, next) => {
  try {
    const comment = await prisma.comment.findUnique({
      where: { id: req.params.id },
    });

    if (!comment) {
      throw new AppError('Comment not found', 404);
    }

    // User can delete their own comment or project admin/owner
    const task = await prisma.task.findUnique({
      where: { id: comment.taskId },
      include: {
        project: true,
      },
    });

    const canDelete =
      comment.userId === req.user!.id ||
      task?.project.ownerId === req.user!.id ||
      (await prisma.projectMember.findFirst({
        where: {
          projectId: task!.projectId,
          userId: req.user!.id,
          role: { in: ['owner', 'admin'] },
        },
      }));

    if (!canDelete) {
      throw new AppError('Insufficient permissions', 403);
    }

    await prisma.comment.delete({
      where: { id: req.params.id },
    });

    res.json({ message: 'Comment deleted successfully' });
  } catch (error) {
    next(error);
  }
});

export default router;
